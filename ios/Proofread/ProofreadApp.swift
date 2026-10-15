import SwiftUI

@main
struct ProofreadApp: App {
    var body: some Scene {
        WindowGroup {
            ComposerView(client: ReplyClient(baseURL: URL(string: "http://127.0.0.1:8000")!))
        }
    }
}
