import SwiftUI
import UIKit

struct ComposerView: View {
    let client: ReplyClient
    @State private var incomingMessage = ""
    @State private var relationship = ""
    @State private var goal = ""
    @State private var draft = ""
    @State private var rewrite = false
    @State private var loading = false
    @State private var candidates: [ReplyCandidate] = []
    @State private var error: String?
    @State private var copiedID: Int?

    private var valid: Bool {
        !incomingMessage.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !relationship.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !goal.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        (!rewrite || !draft.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
    }

    var body: some View {
        NavigationStack {
            Form {
                Section("Message context") {
                    TextField("Incoming message", text: $incomingMessage, axis: .vertical)
                    TextField("Relationship", text: $relationship)
                    TextField("What do you want to achieve?", text: $goal, axis: .vertical)
                }
                Section("Mode") {
                    Toggle("Rewrite my draft", isOn: $rewrite)
                    if rewrite { TextField("Your draft", text: $draft, axis: .vertical) }
                }
                Button(loading ? "Generating…" : "Get three replies") {
                    Task { await requestReplies() }
                }
                .disabled(!valid || loading)
                if let error {
                    Section("Error") { Text(error).foregroundStyle(.red) }
                }
                if !candidates.isEmpty {
                    Section("Suggestions — tap to copy") {
                        ForEach(candidates) { candidate in
                            Button {
                                UIPasteboard.general.string = candidate.text
                                copiedID = candidate.id
                            } label: {
                                VStack(alignment: .leading, spacing: 5) {
                                    Text(candidate.label).font(.caption).foregroundStyle(.secondary)
                                    Text(candidate.text).foregroundStyle(.primary)
                                    if copiedID == candidate.id {
                                        Text("Copied").font(.caption).foregroundStyle(.green)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Proofread")
        }
    }

    @MainActor
    private func requestReplies() async {
        loading = true
        error = nil
        candidates = []
        copiedID = nil
        defer { loading = false }
        do {
            let response = try await client.generate(ReplyRequest(
                mode: rewrite ? "rewrite" : "generate",
                incomingMessage: incomingMessage, relationship: relationship,
                goal: goal, draft: rewrite ? draft : nil
            ))
            candidates = response.candidates
        } catch {
            self.error = error.localizedDescription
        }
    }
}
