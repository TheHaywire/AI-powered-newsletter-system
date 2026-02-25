import Foundation

struct Subscriber: Codable, Identifiable {
    let id: String
    let email: String
    let name: String?
    let subscribedAt: Date?
    let isActive: Bool
    let preferences: SubscriberPreferences?

    enum CodingKeys: String, CodingKey {
        case id, email, name, preferences
        case subscribedAt = "subscribed_at"
        case isActive = "is_active"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = (try? container.decode(String.self, forKey: .id)) ?? UUID().uuidString
        self.email = try container.decode(String.self, forKey: .email)
        self.name = try container.decodeIfPresent(String.self, forKey: .name)
        self.subscribedAt = try container.decodeIfPresent(Date.self, forKey: .subscribedAt)
        self.isActive = (try? container.decode(Bool.self, forKey: .isActive)) ?? true
        self.preferences = try container.decodeIfPresent(SubscriberPreferences.self, forKey: .preferences)
    }
}

struct SubscriberPreferences: Codable {
    let categories: [String]?
    let frequency: String?
    let format: String?
}

struct AddSubscriberRequest: Codable {
    let email: String
    let name: String?
}

struct SubscriberResponse: Codable {
    let success: Bool
    let message: String
    let subscriber: Subscriber?
}

struct SubscriberListResponse: Codable {
    let subscribers: [Subscriber]
    let total: Int
}
