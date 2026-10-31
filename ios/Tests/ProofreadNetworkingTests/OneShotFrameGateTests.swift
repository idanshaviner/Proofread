import Foundation
import XCTest
@testable import ProofreadNetworking

@MainActor
final class OneShotFrameGateTests: XCTestCase {
    func testThresholdWaitsThenConsumesOnceAndAllowsExplicitRearm() async {
        let clock = GateTestClock(100)
        let gate = OneShotFrameGate(clock: { clock.read() })
        let first = token()
        XCTAssertNil(gate.consumeIfReady())
        XCTAssertTrue(gate.arm(first, notBefore: 105, expiresAt: 130))
        XCTAssertFalse(gate.arm(token(), notBefore: 100, expiresAt: 130))
        XCTAssertNil(gate.consumeIfReady())
        clock.set(104.999)
        XCTAssertNil(gate.consumeIfReady())
        clock.set(105)
        XCTAssertEqual(gate.consumeIfReady(), first)
        XCTAssertNil(gate.consumeIfReady())
        let next = token()
        XCTAssertTrue(gate.arm(next, notBefore: 105, expiresAt: 130))
        XCTAssertEqual(gate.consumeIfReady(), next)
    }

    func testImmediateCaptureAllowsThresholdJustBeforeArmTime() async {
        let clock = GateTestClock(100)
        let gate = OneShotFrameGate(clock: { clock.read() })
        let request = token()
        XCTAssertTrue(gate.arm(request, notBefore: 99.99, expiresAt: 130))
        XCTAssertEqual(gate.consumeIfReady(), request)
    }

    func testNonfiniteBoundsExpiredOrUnreachableThresholdNeverArm() async {
        let clock = GateTestClock(100)
        let gate = OneShotFrameGate(clock: { clock.read() })
        let bounds: [(TimeInterval, TimeInterval)] = [
            (.nan, 130), (.infinity, 130), (-.infinity, 130),
            (105, .nan), (105, .infinity), (105, -.infinity),
            (100, 100), (99, 99), (130, 130), (131, 130)
        ]
        for (threshold, expiry) in bounds {
            XCTAssertFalse(gate.arm(token(), notBefore: threshold, expiresAt: expiry))
            XCTAssertNil(gate.consumeIfReady())
        }
        for invalid: TimeInterval in [.nan, .infinity, -.infinity] {
            clock.set(invalid)
            XCTAssertFalse(gate.arm(token(), notBefore: 105, expiresAt: 130))
        }
    }

    func testExactExpiryClearsPendingAndCannotDeliverOldToken() async {
        let clock = GateTestClock(100)
        let gate = OneShotFrameGate(clock: { clock.read() })
        XCTAssertTrue(gate.arm(token(), notBefore: 105, expiresAt: 130))
        clock.set(130)
        XCTAssertNil(gate.consumeIfReady())
        let next = token()
        XCTAssertTrue(gate.arm(next, notBefore: 130, expiresAt: 160))
        XCTAssertEqual(gate.consumeIfReady(), next)
    }

    func testClockBeforeArmOrNonfiniteInvalidatesRatherThanDeliveringLater() async {
        for invalid: TimeInterval in [99, .nan, .infinity, -.infinity] {
            let clock = GateTestClock(100)
            let gate = OneShotFrameGate(clock: { clock.read() })
            XCTAssertTrue(gate.arm(token(), notBefore: 105, expiresAt: 130))
            clock.set(invalid)
            XCTAssertNil(gate.consumeIfReady())
            clock.set(106)
            XCTAssertNil(gate.consumeIfReady())
        }
    }

    func testInvalidateDiscardsPendingWithoutPermanentlyClosingGate() async {
        let clock = GateTestClock(100)
        let gate = OneShotFrameGate(clock: { clock.read() })
        XCTAssertTrue(gate.arm(token(), notBefore: 105, expiresAt: 130))
        gate.invalidate()
        clock.set(106)
        XCTAssertNil(gate.consumeIfReady())
        let next = token()
        XCTAssertTrue(gate.arm(next, notBefore: 106, expiresAt: 130))
        XCTAssertEqual(gate.consumeIfReady(), next)
    }

    func testConcurrentConsumersDeliverOnlyOneToken() async {
        let clock = GateTestClock(100)
        let gate = OneShotFrameGate(clock: { clock.read() })
        let expected = token()
        let delivered = GateTestResults()
        XCTAssertTrue(gate.arm(expected, notBefore: 100, expiresAt: 130))
        DispatchQueue.concurrentPerform(iterations: 64) { _ in
            if let value = gate.consumeIfReady() { delivered.append(value) }
        }
        XCTAssertEqual(delivered.snapshot(), [expected])
    }

    private func token() -> CaptureStudySession.FrameToken {
        CaptureStudySession.FrameToken(sessionID: UUID(), id: UUID())
    }
}

/// Both test helpers protect every mutable field, including the injected clock.
private final class GateTestClock: @unchecked Sendable {
    private let lock = NSLock()
    private var value: TimeInterval
    init(_ value: TimeInterval) { self.value = value }
    func read() -> TimeInterval {
        lock.lock()
        defer { lock.unlock() }
        return value
    }
    func set(_ value: TimeInterval) {
        lock.lock()
        self.value = value
        lock.unlock()
    }
}

private final class GateTestResults: @unchecked Sendable {
    private let lock = NSLock()
    private var values: [CaptureStudySession.FrameToken] = []
    func append(_ value: CaptureStudySession.FrameToken) {
        lock.lock()
        values.append(value)
        lock.unlock()
    }
    func snapshot() -> [CaptureStudySession.FrameToken] {
        lock.lock()
        defer { lock.unlock() }
        return values
    }
}
