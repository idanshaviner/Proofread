import Foundation

/// Local synthetic-study state only. No frames, audio, networking or persistence.
/// Freshness is checked on every operation/read; the native owner must stop on
/// dismissal/interruption and clear any UI text copy at expiry or dismissal.
@MainActor
final class CaptureStudySession {
    struct FrameToken: Equatable, Sendable {
        let sessionID: UUID
        let id: UUID
    }

    private let clock: () -> TimeInterval
    private var activeID: UUID?
    private var startedAt: TimeInterval?
    private var pending: FrameToken?
    private var text: String?

    init(clock: @escaping () -> TimeInterval = { ProcessInfo.processInfo.systemUptime }) {
        self.clock = clock
    }

    var sessionID: UUID? {
        expireIfNeeded()
        return activeID
    }

    var currentText: String? {
        expireIfNeeded()
        return text
    }

    @discardableResult
    func begin() -> UUID {
        stop()
        let id = UUID()
        activeID = id
        startedAt = clock()
        return id
    }

    func requestFrame() -> FrameToken? {
        expireIfNeeded()
        guard let activeID, pending == nil else { return nil }
        let token = FrameToken(sessionID: activeID, id: UUID())
        pending = token
        text = nil
        return token
    }

    @discardableResult
    func complete(_ token: FrameToken, text result: String) -> Bool {
        expireIfNeeded()
        guard token.sessionID == activeID, token == pending else { return false }
        pending = nil
        guard result.unicodeScalars.prefix(10_001).count <= 10_000,
              !result.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return false }
        text = result
        return true
    }

    func stop() {
        activeID = nil
        startedAt = nil
        pending = nil
        text = nil
    }

    func invalidate() {
        stop()
    }

    private func expireIfNeeded() {
        guard let startedAt else { return }
        let elapsed = clock() - startedAt
        if !elapsed.isFinite || elapsed < 0 || elapsed >= 30 {
            stop()
        }
    }
}
