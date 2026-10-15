import Foundation
import XCTest
@testable import ProofreadNetworking

@MainActor
final class ComposerModelTests: XCTestCase {
    func testGenerateAndRewriteCaptureInputAndPublishCurrentResults() async throws {
        for rewrite in [false, true] {
            let harness = GenerationHarness()
            let model = makeModel(harness, rewrite: rewrite)
            model.generate()
            XCTAssertTrue(model.loading)
            await harness.waitForRequests(1)
            XCTAssertEqual(harness.requests[0].mode, rewrite ? "rewrite" : "generate")
            XCTAssertEqual(harness.requests[0].incomingMessage, "Invented invitation")
            XCTAssertEqual(harness.requests[0].draft, rewrite ? "Invented draft" : nil)
            harness.succeed(0, prefix: "current")
            await drain()
            XCTAssertFalse(model.loading)
            XCTAssertEqual(model.candidates.first?.text, "current 1")
            XCTAssertNil(model.error)
            XCTAssertEqual(model.copyCandidate(1), "current 1")
            XCTAssertEqual(model.copiedID, 1)
        }
    }

    func testInvalidGenerateAndBlankRewriteDoNotStartRequest() async {
        let harness = GenerationHarness()
        let model = ComposerModel(generator: harness.generate)
        model.generate()
        XCTAssertFalse(model.loading)
        model.input = validInput(rewrite: true)
        model.input.draft = " \n "
        model.generate()
        await drain()
        XCTAssertFalse(model.loading)
        XCTAssertTrue(harness.requests.isEmpty)
    }

    func testInputLengthBoundsAllowMaximumAndRejectOneScalarOver() {
        for (field, maximum) in inputLimits {
            var input = validInput(rewrite: true)
            input[keyPath: field] = String(repeating: "x", count: maximum)
            XCTAssertTrue(input.isValid)
            input[keyPath: field] += "x"
            XCTAssertFalse(input.isValid)
        }
    }

    func testInputLengthCountsUnicodeScalarsRatherThanGraphemeClusters() {
        // Python len() counts the decomposed e and accent separately. Swift's
        // String.count treats each pair as one user-perceived character.
        for (field, maximum) in inputLimits {
            var input = validInput(rewrite: true)
            let decomposed = String(repeating: "e\u{0301}", count: maximum / 2)
            XCTAssertEqual(decomposed.unicodeScalars.count, maximum)
            XCTAssertEqual(decomposed.count, maximum / 2)
            input[keyPath: field] = decomposed
            XCTAssertTrue(input.isValid)
            input[keyPath: field] += "\u{0301}"
            XCTAssertFalse(input.isValid)
        }
    }

    func testOversizedInputsNeverGenerateButDormantGenerateDraftIsIgnored() async {
        for (field, maximum) in inputLimits {
            let harness = GenerationHarness()
            let model = makeModel(harness, rewrite: true)
            model.input[keyPath: field] = String(repeating: "x", count: maximum + 1)
            model.generate()
            await drain()
            XCTAssertFalse(model.loading)
            XCTAssertTrue(harness.requests.isEmpty)
            // Clean up any request from a regression before leaving the case.
            if !harness.requests.isEmpty { harness.succeed(0) }
        }
        let harness = GenerationHarness()
        let model = makeModel(harness)
        model.input.draft = String(repeating: "x", count: 10_001)
        XCTAssertTrue(model.input.isValid)
        model.generate()
        await harness.waitForRequests(1)
        XCTAssertNil(harness.requests.first?.draft)
        harness.succeed(0)
        await drain()
        XCTAssertEqual(model.candidates.count, 3)
    }

    func testMaximumLengthRequestsRemainValidInBothModes() async {
        for rewrite in [false, true] {
            let harness = GenerationHarness()
            let model = makeModel(harness, rewrite: rewrite)
            for (field, maximum) in inputLimits {
                model.input[keyPath: field] = String(repeating: "x", count: maximum)
            }
            XCTAssertTrue(model.input.isValid)
            model.generate()
            await harness.waitForRequests(1)
            XCTAssertEqual(harness.requests.first?.incomingMessage.unicodeScalars.count, 10_000)
            XCTAssertEqual(harness.requests.first?.relationship.unicodeScalars.count, 200)
            XCTAssertEqual(harness.requests.first?.goal.unicodeScalars.count, 500)
            XCTAssertEqual(harness.requests.first?.draft?.unicodeScalars.count, rewrite ? 10_000 : nil)
            harness.succeed(0)
            await drain()
            XCTAssertFalse(model.loading)
            XCTAssertEqual(model.candidates.count, 3)
        }
    }

    func testEveryInputChangeClearsSuggestionsAndCopiedState() async {
        let changes: [(inout ComposerInput) -> Void] = [
            { $0.incomingMessage += " changed" }, { $0.relationship += " changed" },
            { $0.goal += " changed" }, { $0.draft += " changed" }, { $0.rewrite.toggle() }
        ]
        for change in changes {
            let harness = GenerationHarness()
            let model = makeModel(harness)
            model.generate()
            await harness.waitForRequests(1)
            harness.succeed(0)
            await drain()
            XCTAssertEqual(model.copyCandidate(1), "reply 1")
            change(&model.input)
            XCTAssertTrue(model.candidates.isEmpty)
            XCTAssertNil(model.copiedID)
            XCTAssertNil(model.error)
            XCTAssertFalse(model.loading)
            XCTAssertNil(model.copyCandidate(1))
        }
    }

    func testEditingWhileLoadingCancelsAndRejectsLateSuccess() async {
        let harness = GenerationHarness()
        let model = makeModel(harness)
        model.generate()
        await harness.waitForRequests(1)
        model.input.incomingMessage = "Different invented invitation"
        XCTAssertFalse(model.loading)
        harness.succeed(0, prefix: "stale")
        await drain()
        XCTAssertTrue(model.candidates.isEmpty)
        XCTAssertNil(model.error)
        XCTAssertFalse(model.loading)
        XCTAssertTrue(harness.cancelled[0])
    }

    func testOlderSuccessDoesNotEndNewRequestLoadingOrPublishResults() async {
        let harness = GenerationHarness()
        let model = makeModel(harness)
        model.generate()
        await harness.waitForRequests(1)
        model.input.goal = "Different invented goal"
        model.generate()
        await harness.waitForRequests(2)
        guard harness.requests.count == 2 else {
            harness.succeed(0)
            return XCTFail("Editing should permit a new request")
        }
        harness.succeed(0, prefix: "stale")
        await drain()
        XCTAssertTrue(model.loading)
        XCTAssertTrue(model.candidates.isEmpty)
        harness.succeed(1, prefix: "new")
        await drain()
        XCTAssertFalse(model.loading)
        XCTAssertEqual(model.candidates.first?.text, "new 1")
    }

    func testOlderErrorCannotReplaceNewerSuccess() async {
        let harness = GenerationHarness()
        let model = makeModel(harness)
        model.generate()
        await harness.waitForRequests(1)
        model.input.rewrite = true
        model.generate()
        await harness.waitForRequests(2)
        guard harness.requests.count == 2 else {
            harness.fail(0)
            return XCTFail("Changing mode should permit a new request")
        }
        harness.succeed(1, prefix: "rewrite")
        await drain()
        XCTAssertEqual(model.copyCandidate(1), "rewrite 1")
        harness.fail(0)
        await drain()
        XCTAssertNil(model.error)
        XCTAssertEqual(model.candidates.first?.text, "rewrite 1")
        XCTAssertEqual(model.copiedID, 1)
        XCTAssertFalse(model.loading)
    }

    func testCancellationClearsLoadingAndSuppressesLateErrors() async {
        let harness = GenerationHarness()
        let model = makeModel(harness)
        model.generate()
        await harness.waitForRequests(1)
        model.cancel()
        XCTAssertFalse(model.loading)
        XCTAssertTrue(model.candidates.isEmpty)
        harness.fail(0)
        await drain()
        XCTAssertNil(model.error)
        XCTAssertFalse(model.loading)
        XCTAssertTrue(harness.cancelled[0])
    }

    func testCancellationBeforeTaskStartsNeverInvokesGenerator() async {
        let harness = GenerationHarness()
        let model = makeModel(harness)
        model.generate()
        model.cancel()
        await drain()
        XCTAssertTrue(harness.requests.isEmpty)
        XCTAssertFalse(model.loading)
        // Release a naive implementation's pending continuation during red.
        if !harness.requests.isEmpty {
            harness.succeed(0)
            await drain()
        }
    }

    func testModelReleasedBeforeTaskStartsNeverInvokesGenerator() async {
        let harness = GenerationHarness()
        var model: ComposerModel? = makeModel(harness)
        weak var weakModel = model
        model?.generate()
        model = nil
        XCTAssertNil(weakModel)
        await drain()
        XCTAssertTrue(harness.requests.isEmpty)
        if !harness.requests.isEmpty {
            harness.succeed(0)
            await drain()
        }
    }

    func testCurrentFailureCanRetryAndEditingClearsError() async {
        let harness = GenerationHarness()
        let model = makeModel(harness)
        model.generate()
        await harness.waitForRequests(1)
        harness.fail(0)
        await drain()
        XCTAssertEqual(model.error, ReplyClient.ClientError.http(502).localizedDescription)
        XCTAssertFalse(model.loading)
        model.input.draft += " edited"
        XCTAssertNil(model.error)
        model.generate()
        XCTAssertTrue(model.loading)
        XCTAssertNil(model.error)
        await harness.waitForRequests(2)
        harness.succeed(1)
        await drain()
        XCTAssertFalse(model.loading)
        XCTAssertEqual(model.candidates.count, 3)
    }

    func testUnknownGeneratorErrorsNeverExposeMessageContent() async {
        let harness = GenerationHarness()
        let model = makeModel(harness)
        model.generate()
        await harness.waitForRequests(1)
        harness.fail(0, error: NSError(domain: "SyntheticFailure", code: 1, userInfo: [
            NSLocalizedDescriptionKey: "Invented private message context"
        ]))
        await drain()
        XCTAssertEqual(model.error, ReplyClient.ClientError.connectionFailed.localizedDescription)
        XCTAssertFalse(model.error?.contains("private message") ?? false)
        XCTAssertFalse(model.loading)
    }

    func testCurrentGeneratorCancellationStopsLoadingWithoutAnError() async {
        let harness = GenerationHarness()
        let model = makeModel(harness)
        model.generate()
        await harness.waitForRequests(1)
        harness.fail(0, error: CancellationError())
        await drain()
        XCTAssertNil(model.error)
        XCTAssertTrue(model.candidates.isEmpty)
        XCTAssertFalse(model.loading)
    }

    func testUnchangedInputPreservesCurrentResultsAndOnlyCurrentCandidateCanBeCopied() async {
        let harness = GenerationHarness()
        let model = makeModel(harness)
        model.generate()
        await harness.waitForRequests(1)
        harness.succeed(0)
        await drain()
        let unchanged = model.input
        model.input = unchanged
        XCTAssertEqual(model.candidates.count, 3)
        XCTAssertNil(model.copyCandidate(99))
        XCTAssertNil(model.copiedID)
        XCTAssertEqual(model.copyCandidate(2), "reply 2")
        XCTAssertEqual(model.copiedID, 2)
    }

    private func makeModel(_ harness: GenerationHarness, rewrite: Bool = false) -> ComposerModel {
        let model = ComposerModel(generator: harness.generate)
        model.input = validInput(rewrite: rewrite)
        return model
    }

    private func validInput(rewrite: Bool) -> ComposerInput {
        ComposerInput(incomingMessage: "Invented invitation", relationship: "friend", goal: "make plans", draft: "Invented draft", rewrite: rewrite)
    }

    private var inputLimits: [(WritableKeyPath<ComposerInput, String>, Int)] {
        [(\.incomingMessage, 10_000), (\.relationship, 200), (\.goal, 500), (\.draft, 10_000)]
    }

    private func drain() async {
        for _ in 0..<20 { await Task.yield() }
    }
}

/// Deliberately ignores cancellation until resumed, so identity guards must
/// reject late completions independently of URLSession's cancellation behavior.
@MainActor
private final class GenerationHarness {
    private(set) var requests: [ReplyRequest] = []
    private(set) var cancelled: [Bool] = []
    private var continuations: [Int: CheckedContinuation<ReplyResult, Error>] = [:]

    func generate(_ request: ReplyRequest) async throws -> ReplyResult {
        let index = requests.count
        requests.append(request)
        cancelled.append(false)
        defer { cancelled[index] = Task.isCancelled }
        return try await withCheckedThrowingContinuation { continuations[index] = $0 }
    }

    func waitForRequests(_ count: Int) async {
        for _ in 0..<1000 {
            if requests.count >= count { return }
            await Task.yield()
        }
    }

    func succeed(_ index: Int, prefix: String = "reply") {
        continuations.removeValue(forKey: index)?.resume(returning: ReplyResult(
            candidates: (1...3).map { ReplyCandidate(id: $0, text: "\(prefix) \($0)", label: "Synthetic") },
            provider: "deterministic-mock", personalized: false
        ))
    }

    func fail(_ index: Int, error: Error = ReplyClient.ClientError.http(502)) {
        continuations.removeValue(forKey: index)?.resume(throwing: error)
    }
}
