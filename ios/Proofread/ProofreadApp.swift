import SwiftUI

@main
struct ProofreadApp: App {
    var body: some Scene {
        WindowGroup {
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
