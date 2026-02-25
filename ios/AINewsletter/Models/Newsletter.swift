import Foundation

struct Article: Codable, Identifiable {
    let id: UUID
    let title: String
    let url: String
    let content: String
    let author: String?
    let publishedDate: Date?
    let source: String
    let category: String
    let sentimentScore: Double?
    let relevanceScore: Double?
    let biasScore: Double?

    enum CodingKeys: String, CodingKey {
        case id, title, url, content, author, source, category
        case publishedDate = "published_date"
        case sentimentScore = "sentiment_score"
        case relevanceScore = "relevance_score"
        case biasScore = "bias_score"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = (try? container.decode(UUID.self, forKey: .id)) ?? UUID()
        self.title = try container.decode(String.self, forKey: .title)
        self.url = try container.decode(String.self, forKey: .url)
        self.content = try container.decode(String.self, forKey: .content)
        self.author = try container.decodeIfPresent(String.self, forKey: .author)
        self.publishedDate = try container.decodeIfPresent(Date.self, forKey: .publishedDate)
        self.source = try container.decode(String.self, forKey: .source)
        self.category = try container.decode(String.self, forKey: .category)
        self.sentimentScore = try container.decodeIfPresent(Double.self, forKey: .sentimentScore)
        self.relevanceScore = try container.decodeIfPresent(Double.self, forKey: .relevanceScore)
        self.biasScore = try container.decodeIfPresent(Double.self, forKey: .biasScore)
    }
}

struct NewsletterSection: Codable, Identifiable {
    let id: UUID
    let title: String
    let articles: [Article]

    init(id: UUID = UUID(), title: String, articles: [Article]) {
        self.id = id
        self.title = title
        self.articles = articles
    }

    enum CodingKeys: String, CodingKey {
        case id, title, articles
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = (try? container.decode(UUID.self, forKey: .id)) ?? UUID()
        self.title = try container.decode(String.self, forKey: .title)
        self.articles = try container.decode([Article].self, forKey: .articles)
    }
}

struct NewsletterMetrics: Codable {
    let wordCount: Int
    let readingTimeMinutes: Int
    let articleCount: Int
    let sourceCount: Int
    let averageSentiment: Double?
    let qualityScore: Double?

    enum CodingKeys: String, CodingKey {
        case wordCount = "word_count"
        case readingTimeMinutes = "reading_time_minutes"
        case articleCount = "article_count"
        case sourceCount = "source_count"
        case averageSentiment = "average_sentiment"
        case qualityScore = "quality_score"
    }
}

struct Newsletter: Codable, Identifiable {
    let id: String
    let title: String
    let subtitle: String?
    let theme: String?
    let sections: [NewsletterSection]
    let summary: String?
    let keyInsights: [String]?
    let metrics: NewsletterMetrics?
    let createdAt: Date?
    let status: String?

    enum CodingKeys: String, CodingKey {
        case id, title, subtitle, theme, sections, summary, metrics, status
        case keyInsights = "key_insights"
        case createdAt = "created_at"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = (try? container.decode(String.self, forKey: .id)) ?? UUID().uuidString
        self.title = try container.decode(String.self, forKey: .title)
        self.subtitle = try container.decodeIfPresent(String.self, forKey: .subtitle)
        self.theme = try container.decodeIfPresent(String.self, forKey: .theme)
        self.sections = (try? container.decode([NewsletterSection].self, forKey: .sections)) ?? []
        self.summary = try container.decodeIfPresent(String.self, forKey: .summary)
        self.keyInsights = try container.decodeIfPresent([String].self, forKey: .keyInsights)
        self.metrics = try container.decodeIfPresent(NewsletterMetrics.self, forKey: .metrics)
        self.createdAt = try container.decodeIfPresent(Date.self, forKey: .createdAt)
        self.status = try container.decodeIfPresent(String.self, forKey: .status)
    }
}

struct DashboardStats: Codable {
    let totalNewsletters: Int
    let totalSubscribers: Int
    let totalArticles: Int
    let deliveryRate: Double
    let recentNewsletters: [Newsletter]

    enum CodingKeys: String, CodingKey {
        case totalNewsletters = "total_newsletters"
        case totalSubscribers = "total_subscribers"
        case totalArticles = "total_articles"
        case deliveryRate = "delivery_rate"
        case recentNewsletters = "recent_newsletters"
    }
}

struct GenerationRequest: Codable {
    let theme: String
}

struct GenerationResponse: Codable {
    let success: Bool
    let message: String
    let newsletterId: String?

    enum CodingKeys: String, CodingKey {
        case success, message
        case newsletterId = "newsletter_id"
    }
}
