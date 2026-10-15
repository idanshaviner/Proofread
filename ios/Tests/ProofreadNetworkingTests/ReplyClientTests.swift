import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif
import XCTest
@testable import ProofreadNetworking

final class ReplyClientTests: XCTestCase {
    private var session: URLSession!
    private let baseURL = URL(string: "https://example.invalid/api")!

    override func setUp() {
        super.setUp()
        let configuration = URLSessionConfiguration.ephemeral
        configuration.protocolClasses = [StubURLProtocol.self]
        session = URLSession(configuration: configuration)
    }

    override func tearDown() {
        session.invalidateAndCancel()
        StubURLProtocol.handler = nil
        super.tearDown()
    }

    func testGenerateEncodesBackendContractAndDecodesActualAPIFixture() async throws {
        let data = try fixture("generate")
        StubURLProtocol.handler = { request in
            XCTAssertEqual(request.url?.absoluteString, "https://example.invalid/api/v1/responses")
            XCTAssertEqual(request.httpMethod, "POST")
            XCTAssertEqual(request.value(forHTTPHeaderField: "Content-Type"), "application/json")
            XCTAssertEqual(request.value(forHTTPHeaderField: "Accept"), "application/json")
            XCTAssertEqual(request.timeoutInterval, 45)
            let body = try XCTUnwrap(request.httpBody)
            let payload = try XCTUnwrap(JSONSerialization.jsonObject(with: body) as? [String: Any])
            XCTAssertEqual(payload["mode"] as? String, "generate")
            XCTAssertEqual(payload["incoming_message"] as? String, "Want to meet?")
            XCTAssertEqual(payload["relationship"] as? String, "friend")
            XCTAssertEqual(payload["goal"] as? String, "make plans")
            XCTAssertNil(payload["incomingMessage"])
            XCTAssertNil(payload["draft"])
            return (self.httpResponse(request, status: 200), data)
        }
        let result = try await client().generate(payload())
        XCTAssertEqual(result.candidates.map(\.id), [1, 2, 3])
        XCTAssertEqual(result.candidates.first?.label, "Natural")
        XCTAssertEqual(result.provider, "deterministic-mock")
        XCTAssertFalse(result.personalized)
    }

    func testRewriteEncodesDraftAndDecodesActualAPIFixture() async throws {
        let data = try fixture("rewrite")
        StubURLProtocol.handler = { request in
            let body = try XCTUnwrap(request.httpBody)
            let payload = try XCTUnwrap(JSONSerialization.jsonObject(with: body) as? [String: Any])
            XCTAssertEqual(payload["mode"] as? String, "rewrite")
            XCTAssertEqual(payload["draft"] as? String, "See you soon")
            return (self.httpResponse(request, status: 200), data)
        }
        let result = try await client().generate(payload(rewrite: true))
        XCTAssertEqual(result.candidates.first?.text, "See you soon")
        XCTAssertEqual(result.candidates.count, 3)
    }

    func testValidationErrorsDoNotExposeServerPayload() async throws {
        let data = try fixture("validation-error")
        try await assertFailure(status: 422, data: data, expected: .http(422))
    }

    func testProviderAndOtherServerErrorsDoNotExposeServerPayload() async throws {
        try await assertFailure(status: 502, data: fixture("provider-error"), expected: .http(502))
        for status in [401, 429, 500, 502, 503] {
            try await assertFailure(status: status, data: Data("private conversation and secret".utf8), expected: .http(status))
        }
    }

    func testMalformedAndIncompleteSuccessBodiesReturnSafeError() async throws {
        for body in ["private conversation", "{}", "{\"candidates\":[],\"provider\":\"mock\",\"personalized\":false}"] {
            try await assertFailure(status: 200, data: Data(body.utf8), expected: .invalidResponse)
        }
    }

    func testBlankDuplicateAndMissingCandidateFieldsAreRejected() async throws {
        let original = try XCTUnwrap(JSONSerialization.jsonObject(with: fixture("generate")) as? [String: Any])
        let candidates = try XCTUnwrap(original["candidates"] as? [[String: Any]])
        var mutations: [[String: Any]] = []
        for field in ["text", "label"] {
            var changed = candidates
            changed[0][field] = " \n "
            var value = original
            value["candidates"] = changed
            mutations.append(value)
        }
        for field in ["id", "text"] {
            var changed = candidates
            changed[1][field] = candidates[0][field]
            var value = original
            value["candidates"] = changed
            mutations.append(value)
        }
        for (field, value) in [("text", String(repeating: "x", count: 2001)), ("label", String(repeating: "x", count: 41))] {
            var changed = candidates
            changed[0][field] = value
            var mutation = original
            mutation["candidates"] = changed
            mutations.append(mutation)
        }
        for separator in ["  ", "\t", "\n", "\u{00A0}"] {
            var duplicate = candidates
            duplicate[1]["text"] = "  " + (candidates[0]["text"] as! String).uppercased().replacingOccurrences(of: " ", with: separator) + "\n"
            var normalizedDuplicate = original
            normalizedDuplicate["candidates"] = duplicate
            mutations.append(normalizedDuplicate)
        }
        var missing = original
        missing.removeValue(forKey: "personalized")
        mutations.append(missing)
        for value in mutations {
            try await assertFailure(status: 200, data: JSONSerialization.data(withJSONObject: value), expected: .invalidResponse)
        }
    }

    func testTransportFailuresReturnSafeActionableErrors() async throws {
        for (code, expected) in [(URLError.Code.timedOut, ReplyClient.ClientError.timedOut), (.cannotConnectToHost, .connectionFailed), (.notConnectedToInternet, .connectionFailed)] {
            StubURLProtocol.handler = { _ in
                throw URLError(code, userInfo: [NSLocalizedDescriptionKey: "private conversation"])
            }
            do {
                _ = try await client().generate(payload())
                XCTFail("Expected a transport error")
            } catch let error as ReplyClient.ClientError {
                XCTAssertEqual(error, expected)
                XCTAssertFalse(error.localizedDescription.contains("private conversation"))
            }
        }
    }

    func testCancelledRequestRemainsCancellation() async throws {
        StubURLProtocol.handler = { _ in throw URLError(.cancelled) }
        do {
            _ = try await client().generate(payload())
            XCTFail("Expected cancellation")
        } catch is CancellationError {
            // Cancellation must not masquerade as a server failure.
        }
    }

    func testNonHTTPResponseIsRejected() async throws {
        StubURLProtocol.handler = { request in
            (URLResponse(url: request.url!, mimeType: nil, expectedContentLength: 0, textEncodingName: nil), Data())
        }
        do {
            _ = try await client().generate(payload())
            XCTFail("Expected invalid response")
        } catch let error as ReplyClient.ClientError {
            XCTAssertEqual(error, .invalidResponse)
        }
    }

    /// Opt in only against the local deterministic backend. No model credentials.
    func testLiveBackendGenerateAndRewrite() async throws {
        guard let value = ProcessInfo.processInfo.environment["PROOFREAD_TEST_API_BASE_URL"] else {
            throw XCTSkip("Set PROOFREAD_TEST_API_BASE_URL to run against the local mock API")
        }
        let url = try ReplyClientConfiguration.baseURL(environment: ["PROOFREAD_API_BASE_URL": value], configuredValue: nil)
        let liveClient = ReplyClient(baseURL: url, session: URLSession(configuration: .ephemeral))
        defer { liveClient.session.invalidateAndCancel() }
        for rewrite in [false, true] {
            let result = try await liveClient.generate(payload(rewrite: rewrite))
            XCTAssertEqual(result.provider, "deterministic-mock")
            XCTAssertEqual(result.candidates.count, 3)
            XCTAssertFalse(result.personalized)
        }
        let invalid = ReplyRequest(mode: "rewrite", incomingMessage: "Want to meet?", relationship: "friend", goal: "make plans", draft: nil)
        do {
            _ = try await liveClient.generate(invalid)
            XCTFail("Expected real API validation failure")
        } catch let error as ReplyClient.ClientError {
            XCTAssertEqual(error, .http(422))
        }
    }

    private func client() -> ReplyClient { ReplyClient(baseURL: baseURL, session: session) }

    private func payload(rewrite: Bool = false) -> ReplyRequest {
        ReplyRequest(mode: rewrite ? "rewrite" : "generate", incomingMessage: "Want to meet?", relationship: "friend", goal: "make plans", draft: rewrite ? "See you soon" : nil)
    }

    private func fixture(_ name: String) throws -> Data {
        let url = try XCTUnwrap(Bundle.module.url(forResource: name, withExtension: "json", subdirectory: "Fixtures"))
        return try Data(contentsOf: url)
    }

    private func httpResponse(_ request: URLRequest, status: Int) -> HTTPURLResponse {
        HTTPURLResponse(url: request.url!, statusCode: status, httpVersion: nil, headerFields: ["Content-Type": "application/json"])!
    }

    private func assertFailure(status: Int, data: Data, expected: ReplyClient.ClientError) async throws {
        StubURLProtocol.handler = { request in (self.httpResponse(request, status: status), data) }
        do {
            _ = try await client().generate(payload())
            XCTFail("Expected \(expected)")
        } catch let error as ReplyClient.ClientError {
            XCTAssertEqual(error, expected)
            XCTAssertFalse(error.localizedDescription.contains("private conversation"))
            XCTAssertFalse(error.localizedDescription.contains("secret"))
            XCTAssertFalse(error.localizedDescription.contains("Want to meet?"))
        }
    }
}

private final class StubURLProtocol: URLProtocol {
    // XCTest runs these methods serially. Every test injects an ephemeral session
    // and resets this handler in tearDown; no real network is used by stubs.
    static var handler: ((URLRequest) throws -> (URLResponse, Data))?

    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }

    override func startLoading() {
        do {
            let handler = try XCTUnwrap(Self.handler)
            let (response, data) = try handler(request)
            client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch {
            client?.urlProtocol(self, didFailWithError: error)
        }
    }

    override func stopLoading() {}
}
