import SwiftUI

@main
struct ProofreadApp: App {
    var body: some Scene {
        WindowGroup {
            if ProcessInfo.processInfo.environment["PROOFREAD_CAPTURE_STUDY"] == "1" {
                CaptureStudyView()
            } else {
                switch Result(catching: { try ReplyClientConfiguration.baseURL() }) {
                case .success(let baseURL):
                    ComposerView(client: ReplyClient(baseURL: baseURL))
                case .failure(let error):
                    ContentUnavailableView(
                        "Backend configuration needed",
                        systemImage: "network",
                        description: Text(error.localizedDescription)
                    )
                }
            }
        }
    }
}
