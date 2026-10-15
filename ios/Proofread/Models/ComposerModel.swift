import Foundation
#if canImport(SwiftUI)
import Observation
#endif

struct ComposerInput: Equatable {
    var incomingMessage = ""
    var relationship = ""
    var goal = ""
    var draft = ""
    var rewrite = false

    var isValid: Bool {
        validRequiredField(incomingMessage, maximum: 10_000) &&
        validRequiredField(relationship, maximum: 200) &&
        validRequiredField(goal, maximum: 500) &&
        (!rewrite || validRequiredField(draft, maximum: 10_000))
    }

    private func validRequiredField(_ value: String, maximum: Int) -> Bool {
        // Match the API's Python codepoint limits, including decomposed Unicode.
        !value.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        value.unicodeScalars.count <= maximum
    }

    var request: ReplyRequest {
        ReplyRequest(mode: rewrite ? "rewrite" : "generate", incomingMessage: incomingMessage,
                     relationship: relationship, goal: goal, draft: rewrite ? draft : nil)
    }
}

#if canImport(SwiftUI)
// Apple UI observation is the only platform adapter. State transitions below
// are Foundation-only and exercised by the same tests on Linux.
@Observable
#endif
@MainActor
final class ComposerModel {
    var input = ComposerInput() {
        didSet {
            if input != oldValue { cancel() }
        }
    }
    private(set) var loading = false
    private(set) var candidates: [ReplyCandidate] = []
    private(set) var error: String?
    private(set) var copiedID: Int?

    private let generator: (ReplyRequest) async throws -> ReplyResult
#if canImport(SwiftUI)
    @ObservationIgnored
#endif
    private var task: Task<Void, Never>?
#if canImport(SwiftUI)
    @ObservationIgnored
#endif
    private var requestID: UUID?

    init(generator: @escaping (ReplyRequest) async throws -> ReplyResult) {
        self.generator = generator
    }

    func generate() {
        guard input.isValid, !loading else { return }
        cancel()
        loading = true
        let id = UUID()
        requestID = id
        let payload = input.request
        let generate = generator
        task = Task { @MainActor [weak self] in
            // Edits/disappearance may cancel before this task is first scheduled.
            // Avoid even starting network work for that obsolete request.
            guard !Task.isCancelled, self?.requestID == id else { return }
            do {
                let result = try await generate(payload)
                self?.finish(id, result: .success(result))
            } catch {
                self?.finish(id, result: .failure(error))
            }
        }
    }

    /// Input edits and view disappearance immediately invalidate all old output.
    /// A generator may ignore cancellation, so request identity remains essential.
    func cancel() {
        requestID = nil
        task?.cancel()
        task = nil
        loading = false
        candidates = []
        error = nil
        copiedID = nil
    }

    /// Resolve text from current state so an old view closure cannot copy stale
    /// text after edits or a newer response that reuses candidate identifiers.
    func copyCandidate(_ id: Int) -> String? {
        guard let candidate = candidates.first(where: { $0.id == id }) else { return nil }
        copiedID = id
        return candidate.text
    }

    private func finish(_ id: UUID, result: Result<ReplyResult, Error>) {
        guard requestID == id else { return }
        defer {
            loading = false
            task = nil
            requestID = nil
        }
        guard !Task.isCancelled else { return }
        switch result {
        case .success(let response): candidates = response.candidates
        case .failure(is CancellationError): break
        case .failure(let failure as ReplyClient.ClientError): error = failure.localizedDescription
        case .failure: error = ReplyClient.ClientError.connectionFailed.localizedDescription
        }
    }
}
