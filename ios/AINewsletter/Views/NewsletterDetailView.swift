import SwiftUI

struct NewsletterDetailView: View {
    let newsletterId: String
    @StateObject private var viewModel = NewsletterViewModel()

    var body: some View {
        ScrollView {
            if viewModel.isLoading {
                ProgressView("Loading...")
                    .frame(maxWidth: .infinity, minHeight: 300)
            } else if let newsletter = viewModel.selectedNewsletter {
                VStack(alignment: .leading, spacing: 20) {
                    // Header
                    VStack(alignment: .leading, spacing: 8) {
                        if let theme = newsletter.theme {
                            Text(theme.uppercased())
                                .font(.caption.bold())
                                .foregroundStyle(.accent)
                        }

                        Text(newsletter.title)
                            .font(.title.bold())

                        if let subtitle = newsletter.subtitle {
                            Text(subtitle)
                                .font(.title3)
                                .foregroundStyle(.secondary)
                        }
                    }
                    .padding(.horizontal)

                    // Metrics bar
                    if let metrics = newsletter.metrics {
                        MetricsBar(metrics: metrics)
                    }

                    // Summary
                    if let summary = newsletter.summary {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Summary")
                                .font(.headline)

                            Text(summary)
                                .font(.body)
                                .foregroundStyle(.secondary)
                        }
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
                        .padding(.horizontal)
                    }

                    // Key Insights
                    if let insights = newsletter.keyInsights, !insights.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Key Insights")
                                .font(.headline)
                                .padding(.horizontal)

                            ForEach(Array(insights.enumerated()), id: \.offset) { _, insight in
                                HStack(alignment: .top, spacing: 8) {
                                    Image(systemName: "lightbulb.fill")
                                        .foregroundStyle(.yellow)
                                        .font(.caption)
                                        .padding(.top, 2)

                                    Text(insight)
                                        .font(.subheadline)
                                }
                                .padding(.horizontal)
                            }
                        }
                    }

                    // Sections
                    ForEach(newsletter.sections) { section in
                        SectionView(section: section)
                    }

                    Spacer().frame(height: 20)
                }
                .padding(.vertical)
            } else if let error = viewModel.errorMessage {
                ContentUnavailableView {
                    Label("Error", systemImage: "exclamationmark.triangle")
                } description: {
                    Text(error)
                }
            }
        }
        .navigationTitle("Newsletter")
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await viewModel.loadNewsletter(id: newsletterId)
        }
    }
}

struct MetricsBar: View {
    let metrics: NewsletterMetrics

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 16) {
                MetricChip(icon: "doc.text", label: "\(metrics.articleCount) articles")
                MetricChip(icon: "textformat.size", label: "\(metrics.wordCount) words")
                MetricChip(icon: "clock", label: "\(metrics.readingTimeMinutes) min read")
                MetricChip(icon: "building.2", label: "\(metrics.sourceCount) sources")

                if let quality = metrics.qualityScore {
                    MetricChip(
                        icon: "star.fill",
                        label: String(format: "%.0f%% quality", quality * 100)
                    )
                }
            }
            .padding(.horizontal)
        }
    }
}

struct MetricChip: View {
    let icon: String
    let label: String

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .font(.caption2)
            Text(label)
                .font(.caption)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(.ultraThinMaterial, in: Capsule())
    }
}

struct SectionView: View {
    let section: NewsletterSection

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(section.title)
                .font(.title3.bold())
                .padding(.horizontal)

            ForEach(section.articles) { article in
                ArticleCard(article: article)
            }
        }
    }
}

struct ArticleCard: View {
    let article: Article

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(article.title)
                .font(.subheadline.bold())
                .lineLimit(3)

            Text(article.content)
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(4)

            HStack {
                Label(article.source, systemImage: "globe")
                    .font(.caption2)
                    .foregroundStyle(.accent)

                Spacer()

                if let sentiment = article.sentimentScore {
                    SentimentIndicator(score: sentiment)
                }
            }
        }
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 10))
        .padding(.horizontal)
    }
}

struct SentimentIndicator: View {
    let score: Double

    var color: Color {
        if score > 0.2 { return .green }
        if score < -0.2 { return .red }
        return .gray
    }

    var label: String {
        if score > 0.2 { return "Positive" }
        if score < -0.2 { return "Negative" }
        return "Neutral"
    }

    var body: some View {
        HStack(spacing: 3) {
            Circle()
                .fill(color)
                .frame(width: 6, height: 6)
            Text(label)
                .font(.caption2)
                .foregroundStyle(color)
        }
    }
}
