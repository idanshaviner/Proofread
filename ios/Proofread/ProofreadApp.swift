import SwiftUI

@main
struct ProofreadApp: App {
    var body: some Scene {
        WindowGroup {
            if let baseURL = try? ReplyClientConfiguration.baseURL() {
                ComposerView(client: ReplyClient(baseURL: baseURL))
            } else {
                ContentUnavailableView(
                    "Backend configuration needed",
                    systemImage: "network",
                    description: Text(ReplyClientConfiguration.ConfigurationError.invalidBaseURL.localizedDescription)
                )
            }
        }
    }
}
