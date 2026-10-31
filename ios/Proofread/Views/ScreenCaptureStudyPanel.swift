import SwiftUI

#if canImport(ScreenCaptureKit)
@available(iOS 27.0, *)
@MainActor
struct ScreenCaptureStudyPanel: View {
    @StateObject private var controller = ScreenCaptureStudyController()
    @Environment(\.scenePhase) private var scenePhase
    @State private var crossAppTest = false
    @State private var syntheticOnlyConfirmed = false

    var body: some View {
        Section("System capture · controlled study") {
            Toggle("Test an invented note in another app", isOn: $crossAppTest)
                .disabled(controller.sessionActive)
            if crossAppTest {
                Text("Prepare a NEW Notes note with a unique invented phrase not displayed anywhere in this app. Use a different phrase each run. Close real chats and avoid private notifications. This requests wider screen sharing; it is not a Snapchat test.")
                Toggle("I will display only invented test content", isOn: $syntheticOnlyConfirmed)
                    .disabled(controller.sessionActive)
                Text("After sharing starts, tap the 5-second capture button and immediately switch to your test note. Return here within 20 seconds to inspect the result. The result must contain your unique Notes phrase, not these app instructions, to count as cross-app evidence.")
            } else {
                Text("This mode shares only Proofread's own screen. OCR result text is captured output, not another set of buttons.")
            }
            Text("Audio and camera are disabled. The app saves no video and uploads nothing. Results expire after 30 seconds. iOS may pause background cleanup, so return promptly, press Stop and check the system sharing indicator.")
            Button("Start system sharing prompt") {
                controller.start(currentApplicationOnly: !crossAppTest)
            }
            .disabled(controller.sessionActive || (crossAppTest && !syntheticOnlyConfirmed))
            Button(crossAppTest ? "Capture in 5 seconds · switch to Notes" : "Read one frame locally") {
                if crossAppTest { controller.captureAfterSwitch() }
                else { controller.captureOneFrame() }
            }
            .disabled(!controller.running || controller.capturing)
            Button("Stop capture and clear text", role: .destructive) { controller.stop() }
            Text(controller.status)
                .accessibilityLabel("System capture status: \(controller.status)")
            if !controller.text.isEmpty {
                Text("Captured text — output, not controls")
                    .font(.caption)
                Text(controller.text).textSelection(.enabled)
            }
        }
        .onDisappear { controller.stop() }
        .onChange(of: scenePhase) { _, phase in
            if phase == .background { controller.invalidateForBackground() }
        }
    }
}
#endif
