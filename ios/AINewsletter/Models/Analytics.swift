import Foundation

struct AnalyticsData: Codable {
    let deliveryStats: DeliveryStats
    let engagementStats: EngagementStats
    let contentStats: ContentStats
    let timeSeriesData: [TimeSeriesPoint]

    enum CodingKeys: String, CodingKey {
        case deliveryStats = "delivery_stats"
        case engagementStats = "engagement_stats"
        case contentStats = "content_stats"
        case timeSeriesData = "time_series_data"
    }
}

struct DeliveryStats: Codable {
    let totalSent: Int
    let delivered: Int
    let failed: Int
    let deliveryRate: Double

    enum CodingKeys: String, CodingKey {
        case totalSent = "total_sent"
        case delivered, failed
        case deliveryRate = "delivery_rate"
    }
}

struct EngagementStats: Codable {
    let openRate: Double
    let clickRate: Double
    let unsubscribeRate: Double

    enum CodingKeys: String, CodingKey {
        case openRate = "open_rate"
        case clickRate = "click_rate"
        case unsubscribeRate = "unsubscribe_rate"
    }
}

struct ContentStats: Codable {
    let averageArticles: Double
    let averageWordCount: Double
    let averageReadingTime: Double
    let topCategories: [CategoryCount]
    let averageQualityScore: Double

    enum CodingKeys: String, CodingKey {
        case averageArticles = "average_articles"
        case averageWordCount = "average_word_count"
        case averageReadingTime = "average_reading_time"
        case topCategories = "top_categories"
        case averageQualityScore = "average_quality_score"
    }
}

struct CategoryCount: Codable, Identifiable {
    var id: String { category }
    let category: String
    let count: Int
}

struct TimeSeriesPoint: Codable, Identifiable {
    var id: String { date }
    let date: String
    let newsletters: Int
    let subscribers: Int
    let deliveryRate: Double

    enum CodingKeys: String, CodingKey {
        case date, newsletters, subscribers
        case deliveryRate = "delivery_rate"
    }
}

struct AppSettings: Codable {
    var serverURL: String
    var theme: String
    var notificationsEnabled: Bool
    var autoRefresh: Bool
    var refreshIntervalMinutes: Int

    enum CodingKeys: String, CodingKey {
        case serverURL = "server_url"
        case theme
        case notificationsEnabled = "notifications_enabled"
        case autoRefresh = "auto_refresh"
        case refreshIntervalMinutes = "refresh_interval_minutes"
    }

    static let `default` = AppSettings(
        serverURL: "http://localhost:5000",
        theme: "Technology & AI",
        notificationsEnabled: true,
        autoRefresh: true,
        refreshIntervalMinutes: 30
    )
}
