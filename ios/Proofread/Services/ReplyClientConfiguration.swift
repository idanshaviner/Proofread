import Foundation

enum ReplyClientConfiguration {
    /// Xcode scheme launch variables override the nonsecret Info.plist setting.
    static func baseURL(
        environment: [String: String] = ProcessInfo.processInfo.environment,
        configuredValue: String? = Bundle.main.object(forInfoDictionaryKey: "ProofreadAPIBaseURL") as? String
    ) throws -> URL {
        let value = environment["PROOFREAD_API_BASE_URL"] ?? configuredValue ?? "http://127.0.0.1:8000"
        guard let components = URLComponents(string: value),
              let host = components.host, !host.isEmpty,
              components.user == nil, components.password == nil,
              components.query == nil, components.fragment == nil,
              components.scheme == "https" || (
                  components.scheme == "http" && ["localhost", "127.0.0.1", "[::1]", "::1"].contains(host.lowercased())
              ),
              let url = components.url
        else { throw ConfigurationError.invalidBaseURL }
        return url
    }

    enum ConfigurationError: LocalizedError {
        case invalidBaseURL

        var errorDescription: String? {
            "Set PROOFREAD_API_BASE_URL to an HTTPS endpoint or a local simulator HTTP endpoint."
        }
    }
}
