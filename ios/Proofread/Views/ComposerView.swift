import SwiftUI
import UIKit

@MainActor
struct ComposerView: View {
    @State private var model: ComposerModel

    init(client: ReplyClient) {
        _model = State(initialValue: ComposerModel(generator: client.generate))
    }

    var body: some View {
        NavigationStack {
            Form {
                Section("Message context") {
                    TextField("Incoming message", text: $model.input.incomingMessage, axis: .vertical)
                    TextField("Relationship", text: $model.input.relationship)
                    TextField("What do you want to achieve?", text: $model.input.goal, axis: .vertical)
                }
                Section("Mode") {
                    Toggle("Rewrite my draft", isOn: $model.input.rewrite)
                    if model.input.rewrite { TextField("Your draft", text: $model.input.draft, axis: .vertical) }
                }
                Button(model.loading ? "Generating…" : "Get three replies") {
                    model.generate()
                }
                .disabled(!model.input.isValid || model.loading)
                if let error = model.error {
                    Section("Error") { Text(error).foregroundStyle(.red) }
                }
                if !model.candidates.isEmpty {
                    Section("Suggestions — tap to copy") {
                        ForEach(model.candidates) { candidate in
                            Button {
                                if let text = model.copyCandidate(candidate.id) {
                                    UIPasteboard.general.string = text
                                }
                            } label: {
                                VStack(alignment: .leading, spacing: 5) {
                                    Text(candidate.label).font(.caption).foregroundStyle(.secondary)
                                    Text(candidate.text).foregroundStyle(.primary)
                                    if model.copiedID == candidate.id {
                                        Text("Copied").font(.caption).foregroundStyle(.green)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Proofread")
            .onDisappear { model.cancel() }
        }
    }
}
