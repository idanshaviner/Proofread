import XCTest
@testable import ProofreadNetworking

final class ReplyClientConfigurationTests: XCTestCase {
    func testDefaultSimulatorEndpoint() throws {
        XCTAssertEqual(try ReplyClientConfiguration.baseURL(environment: [:], configuredValue: nil).absoluteString, "http://127.0.0.1:8000")
    }

    func testSchemeEnvironmentOverridesBuildSetting() throws {
        let url = try ReplyClientConfiguration.baseURL(environment: ["PROOFREAD_API_BASE_URL": "https://example.invalid/api"], configuredValue: "https://other.invalid")
        XCTAssertEqual(url.absoluteString, "https://example.invalid/api")
    }

    func testBuildSettingAndLocalNetworkingEndpoints() throws {
        for value in ["https://example.invalid", "http://localhost:8000", "http://127.0.0.1:8000", "http://[::1]:8000"] {
            XCTAssertEqual(try ReplyClientConfiguration.baseURL(environment: [:], configuredValue: value).absoluteString, value)
        }
    }

    func testInvalidEndpointsAreRejectedWithoutEchoingTheirValues() {
        for value in ["", "not a URL", "ftp://example.invalid", "http://example.invalid", "http://192.168.1.2:8000", "https://user:private-secret@example.invalid", "https://example.invalid?token=private-secret", "https://example.invalid#private-secret"] {
            XCTAssertThrowsError(try ReplyClientConfiguration.baseURL(environment: ["PROOFREAD_API_BASE_URL": value], configuredValue: nil)) { error in
                XCTAssertFalse(error.localizedDescription.contains("private-secret"))
            }
        }
    }
}
