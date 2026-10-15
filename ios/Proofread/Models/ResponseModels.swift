import Foundation

struct ReplyRequest: Encodable {
    let mode: String
    let incomingMessage: String
    let relationship: String
    let goal: String
    let draft: String?
    enum CodingKeys: String, CodingKey {
        case mode, relationship, goal, draft
        case incomingMessage = "incoming_message"
    }
}

struct ReplyCandidate: Identifiable, Decodable {
    let id: Int
    let text: String
    let label: String
}

struct ReplyResult: Decodable {
    let candidates: [ReplyCandidate]
    let provider: String
    let personalized: Bool
}
