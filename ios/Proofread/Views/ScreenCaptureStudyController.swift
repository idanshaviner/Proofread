import UIKit
import Combine
@preconcurrency import ScreenCaptureKit
import Vision
import CoreMedia
import CoreVideo

/// Explicit local-only study. API spelling still requires the owner's iOS 27 SDK
/// build; Linux parsing cannot establish capture, permission, or device behavior.
@available(iOS 27.0, *)
@MainActor
final class ScreenCaptureStudyController: NSObject, ObservableObject {
    @Published private(set) var status = "No screen capture is active."
    @Published private(set) var text = ""
    @Published private(set) var capturing = false
    @Published private(set) var running = false

    private let session = CaptureStudySession()
    private let outputQueue = DispatchQueue(label: "Proofread.study.frame", qos: .userInitiated)
    private let ocrQueue = DispatchQueue(label: "Proofread.study.ocr", qos: .userInitiated)
    private var activeID: UUID?
    private var stream: SCStream?
    private var receiver: StudyFrameReceiver?
    private var streamDelegate: StudyStreamDelegate?
    private var pickerObserver: StudyPickerObserver?
    private var expiration: Task<Void, Never>?
    private var backgroundObserver: NSObjectProtocol?
    private var stoppingRequests: Set<UUID> = []
    private var pendingStarts: Set<ObjectIdentifier> = []
    private var ocrWork: StudyOCRWork?
    private var processingFrame = false

    func start(currentApplicationOnly: Bool = true) {
        guard activeID == nil else { return }
        guard stoppingRequests.isEmpty, pendingStarts.isEmpty, !processingFrame else {
            status = "Previous capture cleanup is pending or unconfirmed. If it does not finish, stop sharing in system controls and relaunch this study app."
            return
        }
        let picker = SCContentSharingPicker.shared
        guard picker.isAvailable else {
            status = "System content sharing is unavailable on this device."
            return
        }
        guard !picker.isActive else {
            status = "A system sharing picker is already active. Finish or cancel it first."
            return
        }
        let id = session.begin()
        activeID = id
        text = ""
        status = "Choose the permitted synthetic screen in the system picker."
        let observer = StudyPickerObserver(sessionID: id,
            selected: { [weak self] id, filter, existing in
                Task { @MainActor [weak self] in self?.selected(filter, existing: existing, id: id) }
            }, ended: { [weak self] id in
                Task { @MainActor [weak self] in
                    guard let self, self.isCurrent(id) else { return }
                    self.stop(message: "Picker canceled or unavailable; temporary content cleared.")
                }
            })
        pickerObserver = observer
        let configuration = SCContentSharingPickerConfiguration()
        configuration.showsMicrophoneControl = false
        configuration.showsCameraControl = false
        picker.defaultConfiguration = configuration
        picker.add(observer)
        picker.isActive = true
        expiration = Task { @MainActor [weak self] in
            do { try await Task.sleep(nanoseconds: 30_000_000_000) }
            catch { return }
            guard let self, self.activeID == id else { return }
            self.stop(message: "Study expired after 30 seconds; temporary text cleared.")
        }
        backgroundObserver = NotificationCenter.default.addObserver(
            forName: UIApplication.didEnterBackgroundNotification, object: nil, queue: .main
        ) { [weak self] _ in
            Task { @MainActor [weak self] in
                guard let self, self.activeID == id else { return }
                self.stop(message: "Stopped on background; temporary text cleared.")
            }
        }
        if currentApplicationOnly { picker.presentPickerForCurrentApplication() }
        else { picker.present() }
    }

    func captureOneFrame() {
        guard let id = activeID, isCurrent(id), running, !capturing, !processingFrame,
              let receiver, let token = session.requestFrame() else { return }
        text = ""
        capturing = true
        status = "Waiting for one frame for local OCR…"
        guard receiver.request(token) else {
            stop(message: "A frame could not be requested; study stopped.")
            return
        }
    }

    func stop() {
        stop(message: "Stopped; temporary text cleared. If a system sharing indicator remains, stop sharing in system controls.")
    }

    private func selected(_ filter: SCContentFilter, existing: SCStream?, id: UUID) {
        guard isCurrent(id) else { return }
        guard existing == nil, stream == nil,
              !filter.isMicrophoneEnabled, !filter.isCameraEnabled else {
            stop(message: "Audio, camera, or changed sharing selection was rejected. Study stopped.")
            return
        }
        detachPicker()
        let configuration = SCStreamConfiguration()
        configuration.capturesAudio = false
        configuration.width = 1_280
        configuration.height = 1_280
        let delegate = StudyStreamDelegate { [weak self] stoppedStream in
            Task { @MainActor [weak self] in
                guard let self, self.activeID == id, self.stream === stoppedStream else { return }
                self.stop(message: "System sharing ended; temporary content cleared.")
            }
        }
        let newStream = SCStream(filter: filter, configuration: configuration, delegate: delegate)
        let newReceiver = StudyFrameReceiver { [weak self] token, buffer in
            // The receiver admits only one explicitly requested frame before
            // scheduling this actor handoff. Other frames enqueue no Tasks.
            Task { @MainActor [weak self] in self?.received(buffer, token: token) }
        }
        streamDelegate = delegate
        receiver = newReceiver
        stream = newStream
        do {
            try newStream.addStreamOutput(newReceiver, type: .screen, sampleHandlerQueue: outputQueue)
        } catch {
            stop(message: "Screen output could not be configured. Study stopped.")
            return
        }
        status = "Starting the permitted screen stream…"
        let streamIdentity = ObjectIdentifier(newStream)
        pendingStarts.insert(streamIdentity)
        newStream.startCapture { [weak self] error in
            Task { @MainActor [weak self] in
                guard let self else { newStream.stopCapture { _ in }; return }
                self.pendingStarts.remove(streamIdentity)
                guard self.isCurrent(id), self.stream === newStream else {
                    // A late successful start must never resurrect a stopped
                    // session, even if its earlier stop completed first.
                    self.stopStream(newStream)
                    return
                }
                guard error == nil else {
                    self.stop(message: "Screen sharing could not start. Temporary content cleared.")
                    return
                }
                self.running = true
                self.status = "Sharing active. OCR runs only when you tap Capture one frame."
            }
        }
    }

    private func received(_ buffer: CMSampleBuffer, token: CaptureStudySession.FrameToken) {
        guard isCurrent(token.sessionID), running, capturing, !processingFrame else { return }
        processingFrame = true
        let work = StudyOCRWork()
        ocrWork = work
        status = "Recognizing one frame locally…"
        ocrQueue.async { [weak self] in
            let result = work.recognize(buffer)
            Task { @MainActor [weak self] in
                guard let self else { return }
                self.processingFrame = false
                if self.ocrWork === work { self.ocrWork = nil }
                guard self.isCurrent(token.sessionID) else { return }
                self.capturing = false
                switch result {
                case .success(let recognized):
                    let accepted = self.session.complete(token, text: recognized)
                    self.text = self.session.currentText ?? ""
                    self.status = accepted ? "One frame recognized locally; text expires with this study."
                                           : "No bounded readable text was found. You may capture another frame."
                case .failure:
                    self.stop(message: "Local OCR failed or the frame exceeded safety limits. Study stopped.")
                }
            }
        }
    }

    private func isCurrent(_ id: UUID) -> Bool {
        guard activeID == id else { return false }
        guard session.sessionID == id else {
            stop(message: "Study expired; temporary content cleared.")
            return false
        }
        return true
    }

    private func detachPicker() {
        guard let pickerObserver else { return }
        SCContentSharingPicker.shared.remove(pickerObserver)
        pickerObserver = nil
        SCContentSharingPicker.shared.isActive = false
    }

    private func stop(message: String) {
        activeID = nil
        session.stop()
        expiration?.cancel()
        expiration = nil
        if let backgroundObserver { NotificationCenter.default.removeObserver(backgroundObserver) }
        backgroundObserver = nil
        detachPicker()
        receiver?.invalidate()
        receiver = nil
        ocrWork?.cancel()
        ocrWork = nil
        running = false
        capturing = false
        text = ""
        status = message
        guard let oldStream = stream else { return }
        stream = nil
        streamDelegate = nil
        stopStream(oldStream)
    }

    private func stopStream(_ oldStream: SCStream) {
        // Track each stop invocation separately: a canceled pending start can
        // finish after its first stop and require a second stop of that stream.
        let stopID = UUID()
        stoppingRequests.insert(stopID)
        oldStream.stopCapture { [weak self] error in
            Task { @MainActor [weak self] in
                guard let self else { return }
                guard error == nil else {
                    // An uncertain OS stop must not permit a second stream.
                    // Keep this request as a restart barrier until app relaunch.
                    if self.activeID == nil {
                        self.status = "Local processing stopped, but system stop was not confirmed. Stop sharing in system controls and relaunch this study app before another session."
                    }
                    return
                }
                self.stoppingRequests.remove(stopID)
            }
        }
    }
}

@available(iOS 27.0, *)
private final class StudyPickerObserver: NSObject, SCContentSharingPickerObserver {
    private let sessionID: UUID
    private let selected: (UUID, SCContentFilter, SCStream?) -> Void
    private let ended: (UUID) -> Void

    init(sessionID: UUID, selected: @escaping (UUID, SCContentFilter, SCStream?) -> Void,
         ended: @escaping (UUID) -> Void) {
        self.sessionID = sessionID
        self.selected = selected
        self.ended = ended
    }

    func contentSharingPicker(_ picker: SCContentSharingPicker, didCancelFor stream: SCStream?) {
        ended(sessionID)
    }

    func contentSharingPicker(_ picker: SCContentSharingPicker, didUpdateWith filter: SCContentFilter, for stream: SCStream?) {
        selected(sessionID, filter, stream)
    }

    func contentSharingPickerStartDidFailWithError(_ error: Error) { ended(sessionID) }
}

@available(iOS 27.0, *)
private final class StudyStreamDelegate: NSObject, SCStreamDelegate {
    private let stopped: (SCStream) -> Void
    init(stopped: @escaping (SCStream) -> Void) { self.stopped = stopped }
    func stream(_ stream: SCStream, didStopWithError error: Error) { stopped(stream) }
}

@available(iOS 27.0, *)
private final class StudyFrameReceiver: NSObject, SCStreamOutput {
    private let lock = NSLock()
    private var pending: CaptureStudySession.FrameToken?
    private var callback: ((CaptureStudySession.FrameToken, CMSampleBuffer) -> Void)?

    init(callback: @escaping (CaptureStudySession.FrameToken, CMSampleBuffer) -> Void) {
        self.callback = callback
    }

    func request(_ token: CaptureStudySession.FrameToken) -> Bool {
        lock.lock()
        defer { lock.unlock() }
        guard callback != nil, pending == nil else { return false }
        pending = token
        return true
    }

    func invalidate() {
        lock.lock()
        pending = nil
        callback = nil
        lock.unlock()
    }

    func stream(_ stream: SCStream, didOutputSampleBuffer sampleBuffer: CMSampleBuffer, of outputType: SCStreamOutputType) {
        guard outputType == .screen else { return }
        lock.lock()
        guard let token = pending, let deliver = callback else { lock.unlock(); return }
        pending = nil
        lock.unlock()
        deliver(token, sampleBuffer)
    }
}

private final class StudyOCRWork {
    private let lock = NSLock()
    private var canceled = false
    private var request: VNRecognizeTextRequest?
    private enum Failure: Error { case rejectedFrame }

    func cancel() {
        lock.lock()
        canceled = true
        request?.cancel()
        lock.unlock()
    }

    func recognize(_ buffer: CMSampleBuffer) -> Result<String, Error> {
        guard CMSampleBufferIsValid(buffer), CMSampleBufferDataIsReady(buffer),
              let image = CMSampleBufferGetImageBuffer(buffer) else { return .failure(Failure.rejectedFrame) }
        let width = CVPixelBufferGetWidth(image)
        let height = CVPixelBufferGetHeight(image)
        guard width > 0, height > 0, width <= 4_096, height <= 4_096,
              width <= 4_000_000 / height,
              CVPixelBufferGetDataSize(image) <= 16_777_216 else { return .failure(Failure.rejectedFrame) }
        let recognition = VNRecognizeTextRequest()
        recognition.recognitionLevel = .accurate
        recognition.recognitionLanguages = ["en-US"]
        recognition.usesLanguageCorrection = false
        lock.lock()
        guard !canceled else { lock.unlock(); return .failure(CancellationError()) }
        request = recognition
        lock.unlock()
        defer {
            lock.lock()
            request = nil
            lock.unlock()
        }
        do {
            try VNImageRequestHandler(cvPixelBuffer: image, options: [:]).perform([recognition])
            lock.lock()
            let wasCanceled = canceled
            lock.unlock()
            guard !wasCanceled else { return .failure(CancellationError()) }
            var lines: [String] = []
            var scalarCount = 0
            for observation in (recognition.results ?? []).prefix(10_001) {
                guard let line = observation.topCandidates(1).first?.string else { continue }
                scalarCount += line.unicodeScalars.prefix(10_001).count + (lines.isEmpty ? 0 : 1)
                guard scalarCount <= 10_000 else { return .failure(Failure.rejectedFrame) }
                lines.append(line)
            }
            return .success(lines.joined(separator: "\n"))
        } catch { return .failure(Failure.rejectedFrame) }
    }
}
