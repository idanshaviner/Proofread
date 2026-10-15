import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

struct ReplyClient {
    let baseURL: URL
    let session: URLSession

    init(baseURL: URL, session: URLSession = URLSession(configuration: .ephemeral)) {
        self.baseURL = baseURL
        self.session = session
    }

    func generate(_ requestPayload: ReplyRequest) async throws -> ReplyResult {
        var request = URLRequest(url: baseURL.appendingPathComponent("v1/responses"))
        request.httpMethod = "POST"
        request.timeoutInterval = 45
        request.cachePolicy = .reloadIgnoringLocalCacheData
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.httpBody = try JSONEncoder().encode(requestPayload)
        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch let error as URLError {
            if error.code == .cancelled { throw CancellationError() }
            throw error.code == .timedOut ? ClientError.timedOut : ClientError.connectionFailed
        } catch is CancellationError {
            throw CancellationError()
        } catch {
            throw ClientError.connectionFailed
        }
        guard let http = response as? HTTPURLResponse else { throw ClientError.invalidResponse }
        guard (200..<300).contains(http.statusCode) else { throw ClientError.http(http.statusCode) }
        // Never surface server payloads or DecodingError context, which may contain
        // private input echoed by a server or an intermediary.
        guard let result = try? JSONDecoder().decode(ReplyResult.self, from: data),
              result.candidates.count == 3,
              Set(result.candidates.map(\.id)).count == 3,
              Set(result.candidates.map {
                  $0.text.split(whereSeparator: \.isWhitespace).joined(separator: " ")
                      .folding(options: .caseInsensitive, locale: Locale(identifier: "en_US_POSIX"))
              }).count == 3,
              result.candidates.allSatisfy({
                  !$0.text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
                  $0.text.unicodeScalars.count <= 2000 &&
                  !$0.label.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
                  $0.label.unicodeScalars.count <= 40
              }),
              !result.provider.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        else { throw ClientError.invalidResponse }
        return result
    }

    enum ClientError: LocalizedError, Equatable {
        case invalidResponse, http(Int), timedOut, connectionFailed
        var errorDescription: String? {
            switch self {
            case .invalidResponse: return "Could not read server response."
            case .timedOut: return "The request timed out. Please try again."
            case .connectionFailed: return "Could not connect to Proofread. Check your connection and try again."
            case .http(422): return "Check the message, relationship, goal, and draft, then try again."
            case .http(429): return "Too many requests. Please try again shortly."
            case .http(502), .http(503): return "Reply generation is temporarily unavailable. Please try again."
            case .http(let status): return "Server error (HTTP \(status))."
            }
        }
    }
}
