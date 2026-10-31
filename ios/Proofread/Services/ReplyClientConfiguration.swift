import Foundation

enum ReplyClientConfiguration {
    private static var runningOnPhysicalDevice: Bool {
#if os(iOS) && !targetEnvironment(simulator)
        return true
#else
        return false
#endif
    }

    /// Xcode scheme launch variables override the nonsecret Info.plist setting.
    static func baseURL(
        environment: [String: String] = ProcessInfo.processInfo.environment,
        configuredValue: String? = Bundle.main.object(forInfoDictionaryKey: "ProofreadAPIBaseURL") as? String,
        physicalDevice: Bool = runningOnPhysicalDevice
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
        if physicalDevice, ["localhost", "127.0.0.1", "[::1]", "::1"].contains(host.lowercased()) {
            throw ConfigurationError.physicalDeviceRequiresServer
        }
        return url
    }

    enum ConfigurationError: LocalizedError {
        case invalidBaseURL, physicalDeviceRequiresServer

        var errorDescription: String? {
            switch self {
            case .invalidBaseURL:
                return "Set PROOFREAD_API_BASE_URL to an HTTPS endpoint or a local simulator HTTP endpoint."
            case .physicalDeviceRequiresServer:
                return "This build points to a simulator-only backend. On your iPhone, localhost refers to the phone, not your Mac. Configure a reachable HTTPS Proofread backend in the Xcode build setting. The offline keyboard examples do not need a backend."
            }
        }
    }
}
