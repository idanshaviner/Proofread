import Foundation

/// Partial editable-field context, never a conversation transcript. Without a
/// document identifier, identical context in different hosts cannot be separated;
/// the platform adapter must also invalidate on text/selection/lifecycle changes.
struct KeyboardContextSnapshot: Equatable {
    let before: String?
    let after: String?
    let selection: String?
    let documentIdentifier: UUID?

    init(before: String?, after: String?, selection: String?, documentIdentifier: UUID? = nil) {
        self.before = before
        self.after = after
        self.selection = selection
        self.documentIdentifier = documentIdentifier
    }

    static func == (lhs: Self, rhs: Self) -> Bool {
        exact(lhs.before, rhs.before) && exact(lhs.after, rhs.after) &&
        exact(lhs.selection, rhs.selection) && lhs.documentIdentifier == rhs.documentIdentifier
    }

    private static func exact(_ lhs: String?, _ rhs: String?) -> Bool {
        switch (lhs, rhs) {
        case (nil, nil): return true
        case let (.some(left), .some(right)): return left.utf8.elementsEqual(right.utf8)
        default: return false
        }
    }

    fileprivate var allowsInsertion: Bool {
        guard before != nil || after != nil || selection != nil,
              selection?.isEmpty != false else { return false }
        var remaining = 10_000
        for text in [before, after, selection].compactMap({ $0 }) {
            let count = text.unicodeScalars.prefix(remaining + 1).count
            guard count <= remaining else { return false }
            remaining -= count
        }
        return true
    }
}

enum KeyboardPrototypeMode {
    case generate, rewrite
}

/// Offline fixtures only: no network, persistence, text rewriting or deletion.
/// Returned text is for one explicit insertion; the caller owns the document proxy.
@MainActor
final class KeyboardPrototypeModel {
    private(set) var candidates: [ReplyCandidate] = []
    private var capturedContext: KeyboardContextSnapshot?
    private var nextCandidateID = 1

    func capture(_ context: KeyboardContextSnapshot, mode: KeyboardPrototypeMode = .generate) {
        invalidate()
        guard context.allowsInsertion, nextCandidateID <= Int.max - 3 else { return }
        let texts: [String]
        switch mode {
        case .generate:
            texts = ["Synthetic reply one.", "Synthetic reply two.", "Synthetic reply three."]
        case .rewrite:
            texts = ["Synthetic rewrite one.", "Synthetic rewrite two.", "Synthetic rewrite three."]
        }
        capturedContext = context
        candidates = texts.enumerated().map { index, text in
            ReplyCandidate(id: nextCandidateID + index, text: text, label: "Synthetic \(index + 1)")
        }
        nextCandidateID += 3
    }

    func invalidate() {
        capturedContext = nil
        candidates = []
    }

    func takeCandidate(_ id: Int, currentContext: KeyboardContextSnapshot) -> String? {
        defer { invalidate() }
        guard currentContext.allowsInsertion, capturedContext == currentContext,
              let candidate = candidates.first(where: { $0.id == id }) else { return nil }
        return candidate.text
    }
}
