import Foundation
import XCTest
@testable import ProofreadNetworking

@MainActor
final class CaptureStudySessionTests: XCTestCase {
    func testExplicitBeginAndSinglePendingFrameAreRequired() async throws {
        let session = CaptureStudySession()
        XCTAssertNil(session.sessionID)
        XCTAssertNil(session.currentText)
        XCTAssertNil(session.requestFrame())
        let id = session.begin()
        let token = try XCTUnwrap(session.requestFrame())
        XCTAssertEqual(token.sessionID, id)
        XCTAssertNil(session.requestFrame())
        XCTAssertTrue(session.complete(token, text: "Invented local text"))
        XCTAssertEqual(session.currentText, "Invented local text")
        XCTAssertFalse(session.complete(token, text: "Duplicate result"))
        XCTAssertEqual(session.currentText, "Invented local text")
    }

    func testBeginningAgainRejectsOldResultsWithoutDisturbingNewPendingFrame() async throws {
        let session = CaptureStudySession()
        let firstID = session.begin()
        let firstToken = try XCTUnwrap(session.requestFrame())
        let secondID = session.begin()
        XCTAssertNotEqual(firstID, secondID)
        let secondToken = try XCTUnwrap(session.requestFrame())
        XCTAssertFalse(session.complete(firstToken, text: "Old result"))
        XCTAssertNil(session.currentText)
        XCTAssertTrue(session.complete(secondToken, text: "Current result"))
        XCTAssertEqual(session.currentText, "Current result")
    }

    func testNextFrameClearsOldTextAndOldTokenCannotConsumeNewWork() async throws {
        let session = CaptureStudySession()
        session.begin()
        let first = try XCTUnwrap(session.requestFrame())
        XCTAssertTrue(session.complete(first, text: "First result"))
        let next = try XCTUnwrap(session.requestFrame())
        XCTAssertNil(session.currentText)
        XCTAssertNotEqual(first, next)
        XCTAssertFalse(session.complete(first, text: "Late duplicate"))
        XCTAssertTrue(session.complete(next, text: "Second result"))
    }

    func testSessionExpiresAtThirtySecondsWithoutCompletionExtendingIt() async throws {
        var now: TimeInterval = 100
        let session = CaptureStudySession(clock: { now })
        session.begin()
        let token = try XCTUnwrap(session.requestFrame())
        now = 129.99
        XCTAssertTrue(session.complete(token, text: "Fresh result"))
        XCTAssertEqual(session.currentText, "Fresh result")
        now = 130
        XCTAssertNil(session.currentText)
        XCTAssertNil(session.sessionID)
        XCTAssertNil(session.requestFrame())
        XCTAssertFalse(session.complete(token, text: "Expired result"))
    }

    func testExpiredPendingFrameCannotPublishText() async throws {
        var now: TimeInterval = 100
        let session = CaptureStudySession(clock: { now })
        session.begin()
        let token = try XCTUnwrap(session.requestFrame())
        now = 131
        XCTAssertFalse(session.complete(token, text: "Expired text"))
        XCTAssertNil(session.currentText)
        XCTAssertNil(session.sessionID)
    }

    func testStopAndInvalidateClearTextAndRejectLateResults() async throws {
        for invalidate in [false, true] {
            let session = CaptureStudySession()
            session.begin()
            let completed = try XCTUnwrap(session.requestFrame())
            XCTAssertTrue(session.complete(completed, text: "Transient result"))
            if invalidate { session.invalidate() } else { session.stop() }
            XCTAssertNil(session.currentText)
            XCTAssertNil(session.sessionID)
            XCTAssertNil(session.requestFrame())
            session.begin()
            let pending = try XCTUnwrap(session.requestFrame())
            if invalidate { session.invalidate() } else { session.stop() }
            XCTAssertFalse(session.complete(pending, text: "Late after stop"))
            XCTAssertNil(session.currentText)
        }
    }

    func testOutputBoundsCountScalarsAndInvalidOutputConsumesOnlyItsPendingSlot() async throws {
        let session = CaptureStudySession()
        session.begin()
        let maximum = String(repeating: "e\u{0301}", count: 5_000)
        let token = try XCTUnwrap(session.requestFrame())
        XCTAssertTrue(session.complete(token, text: maximum))
        XCTAssertEqual(session.currentText, maximum)
        for invalid in ["", " \n\t", maximum + "x", String(repeating: "x", count: 100_000)] {
            let pending = try XCTUnwrap(session.requestFrame())
            XCTAssertFalse(session.complete(pending, text: invalid))
            XCTAssertNil(session.currentText)
        }
        let valid = try XCTUnwrap(session.requestFrame())
        XCTAssertTrue(session.complete(valid, text: "Retry succeeds"))
    }

    func testBackwardOrNonfiniteClockFailsClosed() async throws {
        for invalid: TimeInterval in [99, .infinity, .nan] {
            var now: TimeInterval = 100
            let session = CaptureStudySession(clock: { now })
            session.begin()
            let pending = try XCTUnwrap(session.requestFrame())
            now = invalid
            XCTAssertFalse(session.complete(pending, text: "Unreliable freshness"))
            XCTAssertNil(session.currentText)
            XCTAssertNil(session.sessionID)
        }
    }
}
