import Foundation
import XCTest
@testable import ProofreadNetworking

@MainActor
final class KeyboardPrototypeModelTests: XCTestCase {
    func testBothModesPublishFixedSyntheticCandidatesWithoutEchoingContext() async throws {
        let context = snapshot(before: "SYNTHETIC_PRIVATE_MARKER")
        for mode in [KeyboardPrototypeMode.generate, .rewrite] {
            let model = KeyboardPrototypeModel()
            model.capture(context, mode: mode)
            XCTAssertEqual(model.candidates.count, 3)
            XCTAssertEqual(Set(model.candidates.map(\.id)).count, 3)
            XCTAssertTrue(model.candidates.allSatisfy { $0.text.hasPrefix("Synthetic ") })
            XCTAssertFalse(model.candidates.contains { $0.text.contains("SYNTHETIC_PRIVATE_MARKER") })
        }
    }

    func testExactSnapshotAllowsOneInsertionThenConsumesAllSuggestions() async throws {
        let model = KeyboardPrototypeModel()
        let context = snapshot()
        model.capture(context)
        let candidate = try XCTUnwrap(model.candidates.first)
        XCTAssertEqual(model.takeCandidate(candidate.id, currentContext: context), candidate.text)
        XCTAssertTrue(model.candidates.isEmpty)
        XCTAssertNil(model.takeCandidate(candidate.id, currentContext: context))
    }

    func testChangedBeforeAfterSelectionOrDocumentFailsClosed() async throws {
        let context = snapshot()
        let changes = [
            snapshot(before: "Changed", documentIdentifier: context.documentIdentifier),
            snapshot(after: "Changed", documentIdentifier: context.documentIdentifier),
            snapshot(selection: "Changed", documentIdentifier: context.documentIdentifier),
            snapshot(documentIdentifier: UUID()),
            snapshot(documentIdentifier: nil),
        ]
        for changed in changes {
            let model = KeyboardPrototypeModel()
            model.capture(context)
            let id = try XCTUnwrap(model.candidates.first?.id)
            XCTAssertNil(model.takeCandidate(id, currentContext: changed))
            XCTAssertTrue(model.candidates.isEmpty)
            XCTAssertNil(model.takeCandidate(id, currentContext: context))
        }
    }

    func testUnavailableContextCannotCaptureOrInsertEvenWithDocumentIdentity() async {
        let model = KeyboardPrototypeModel()
        let unavailable = KeyboardContextSnapshot(before: nil, after: nil, selection: nil,
                                                   documentIdentifier: UUID())
        model.capture(unavailable)
        XCTAssertTrue(model.candidates.isEmpty)
        XCTAssertNil(model.takeCandidate(1, currentContext: unavailable))
    }

    func testKnownEmptyContextAllowsInsertionWithNilOrEmptySelection() async throws {
        for selection: String? in [nil, ""] {
            let model = KeyboardPrototypeModel()
            let context = KeyboardContextSnapshot(before: "", after: "", selection: selection)
            model.capture(context)
            let id = try XCTUnwrap(model.candidates.first?.id)
            XCTAssertNotNil(model.takeCandidate(id, currentContext: context))
        }
    }

    func testActiveSelectionNeverAllowsImplicitReplacement() async {
        let model = KeyboardPrototypeModel()
        let context = snapshot(selection: "Selected invented text")
        model.capture(context, mode: .rewrite)
        XCTAssertTrue(model.candidates.isEmpty)
        XCTAssertNil(model.takeCandidate(1, currentContext: context))
    }

    func testInvalidCandidateAndExplicitInvalidationDiscardSuggestions() async throws {
        let model = KeyboardPrototypeModel()
        let context = snapshot()
        model.capture(context)
        XCTAssertNil(model.takeCandidate(-1, currentContext: context))
        XCTAssertTrue(model.candidates.isEmpty)
        model.capture(context)
        let id = try XCTUnwrap(model.candidates.first?.id)
        model.invalidate()
        XCTAssertTrue(model.candidates.isEmpty)
        XCTAssertNil(model.takeCandidate(id, currentContext: context))
    }

    func testRecaptureDoesNotReuseStaleCandidateIdentity() async throws {
        let model = KeyboardPrototypeModel()
        let context = snapshot()
        model.capture(context)
        let oldID = try XCTUnwrap(model.candidates.first?.id)
        model.capture(context, mode: .rewrite)
        XCTAssertFalse(model.candidates.contains { $0.id == oldID })
        XCTAssertNil(model.takeCandidate(oldID, currentContext: context))
    }

    func testContextBoundsCountScalarsAndRejectCombinedExcess() async {
        let model = KeyboardPrototypeModel()
        let maximum = String(repeating: "e\u{0301}", count: 5_000)
        model.capture(KeyboardContextSnapshot(before: maximum, after: nil, selection: nil))
        XCTAssertEqual(model.candidates.count, 3)
        model.capture(KeyboardContextSnapshot(before: maximum, after: "x", selection: nil))
        XCTAssertTrue(model.candidates.isEmpty)
        model.capture(KeyboardContextSnapshot(before: String(repeating: "x", count: 100_000),
                                               after: nil, selection: nil))
        XCTAssertTrue(model.candidates.isEmpty)
    }

    func testCanonicallyEquivalentButChangedScalarsInvalidateSnapshot() async throws {
        let model = KeyboardPrototypeModel()
        let context = snapshot(before: "Café")
        let changed = snapshot(before: "Cafe\u{0301}", documentIdentifier: context.documentIdentifier)
        XCTAssertEqual(context.before, changed.before) // Swift String canonical equality.
        XCTAssertNotEqual(context, changed) // Cursor context must match exact content.
        model.capture(context)
        let id = try XCTUnwrap(model.candidates.first?.id)
        XCTAssertNil(model.takeCandidate(id, currentContext: changed))
    }

    private func snapshot(before: String? = "Invented draft", after: String? = "After cursor",
                          selection: String? = nil, documentIdentifier: UUID? = UUID()) -> KeyboardContextSnapshot {
        KeyboardContextSnapshot(before: before, after: after, selection: selection,
                                documentIdentifier: documentIdentifier)
    }
}
