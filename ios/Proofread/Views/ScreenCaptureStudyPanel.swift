import SwiftUI

#if canImport(ScreenCaptureKit)
@available(iOS 27.0, *)
@MainActor
struct ScreenCaptureStudyPanel: View {
    @StateObject private var controller = ScreenCaptureStudyController()
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        Section("System capture · first synthetic test") {
            Text("This first test shares only Proofread's own screen through the system prompt. It does not read another app or generate replies. Use invented text only.")
            Text("Audio and camera are disabled. No video is saved or uploaded. Capture stops after 30 seconds, when you leave the app, or when you press Stop.")
            Button("Start system sharing prompt") {
                controller.start(currentApplicationOnly: true)
            }
            .disabled(controller.capturing || controller.running)
            Button("Read one frame locally") { controller.captureOneFrame() }
                .disabled(!controller.running || controller.capturing)
            Button("Stop capture and clear text", role: .destructive) { controller.stop() }
            Text(controller.status)
                .accessibilityLabel("System capture status: \(controller.status)")
            if !controller.text.isEmpty {
                Text("Local OCR result — temporary")
                    .font(.caption)
                Text(controller.text).textSelection(.enabled)
            }
        }
        .onDisappear { controller.stop() }
        .onChange(of: scenePhase) { _, phase in
            if phase == .background { controller.stop() }
        }
    }
}
#endif
