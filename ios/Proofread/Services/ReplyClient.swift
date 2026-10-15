import Foundation

struct ReplyClient {
    let baseURL: URL

    func generate(_ requestPayload: ReplyRequest) async throws -> ReplyResult {
        var request = URLRequest(url: baseURL.appendingPathComponent("v1/responses"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(requestPayload)
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse else { throw ClientError.invalidResponse }
        guard (200..<300).contains(http.statusCode) else { throw ClientError.http(http.statusCode) }
        return try JSONDecoder().decode(ReplyResult.self, from: data)
    }

    enum ClientError: LocalizedError {
        case invalidResponse, http(Int)
        var errorDescription: String? {
            switch self {
            case .invalidResponse: return "Could not read server response."
            case .http(let status): return "Server error (HTTP \(status))."
            }
        }
    }
}
