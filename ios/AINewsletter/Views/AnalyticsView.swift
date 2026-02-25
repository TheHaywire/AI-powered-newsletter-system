import SwiftUI

struct AnalyticsView: View {
    @StateObject private var viewModel = AnalyticsViewModel()

    var body: some View {
        NavigationStack {
            ScrollView {
                if viewModel.isLoading && viewModel.analytics == nil {
                    ProgressView("Loading analytics...")
                        .frame(maxWidth: .infinity, minHeight: 300)
                } else if let error = viewModel.errorMessage, viewModel.analytics == nil {
                    ContentUnavailableView {
                        Label("Error", systemImage: "exclamationmark.triangle")
                    } description: {
                        Text(error)
                    } actions: {
                        Button("Retry") {
                            Task { await viewModel.loadAnalytics() }
                        }
                    }
                } else if let analytics = viewModel.analytics {
                    VStack(spacing: 24) {
                        // Delivery stats
                        AnalyticsSectionCard(title: "Delivery", icon: "paperplane.fill") {
                            HStack(spacing: 20) {
                                AnalyticsStat(
                                    value: "\(analytics.deliveryStats.totalSent)",
                                    label: "Sent"
                                )
                                AnalyticsStat(
                                    value: "\(analytics.deliveryStats.delivered)",
                                    label: "Delivered"
                                )
                                AnalyticsStat(
                                    value: "\(analytics.deliveryStats.failed)",
                                    label: "Failed"
                                )
                                AnalyticsStat(
                                    value: String(format: "%.0f%%", analytics.deliveryStats.deliveryRate * 100),
                                    label: "Rate"
                                )
                            }
                        }

                        // Engagement stats
                        AnalyticsSectionCard(title: "Engagement", icon: "hand.tap.fill") {
                            HStack(spacing: 20) {
                                RingChart(
                                    value: analytics.engagementStats.openRate,
                                    label: "Opens",
                                    color: .blue
                                )
                                RingChart(
                                    value: analytics.engagementStats.clickRate,
                                    label: "Clicks",
                                    color: .green
                                )
                                RingChart(
                                    value: analytics.engagementStats.unsubscribeRate,
                                    label: "Unsubs",
                                    color: .red
                                )
                            }
                            .frame(height: 100)
                        }

                        // Content stats
                        AnalyticsSectionCard(title: "Content Quality", icon: "doc.text.magnifyingglass") {
                            VStack(spacing: 12) {
                                ContentStatRow(
                                    label: "Avg. Articles",
                                    value: String(format: "%.1f", analytics.contentStats.averageArticles)
                                )
                                ContentStatRow(
                                    label: "Avg. Word Count",
                                    value: String(format: "%.0f", analytics.contentStats.averageWordCount)
                                )
                                ContentStatRow(
                                    label: "Avg. Reading Time",
                                    value: String(format: "%.0f min", analytics.contentStats.averageReadingTime)
                                )
                                ContentStatRow(
                                    label: "Quality Score",
                                    value: String(format: "%.0f%%", analytics.contentStats.averageQualityScore * 100)
                                )
                            }
                        }

                        // Top categories
                        if !analytics.contentStats.topCategories.isEmpty {
                            AnalyticsSectionCard(title: "Top Categories", icon: "tag.fill") {
                                VStack(spacing: 8) {
                                    ForEach(analytics.contentStats.topCategories) { cat in
                                        HStack {
                                            Text(cat.category)
                                                .font(.subheadline)
                                            Spacer()
                                            Text("\(cat.count)")
                                                .font(.subheadline.bold())
                                                .foregroundStyle(.accent)
                                        }
                                    }
                                }
                            }
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Analytics")
            .refreshable {
                await viewModel.loadAnalytics()
            }
            .task {
                await viewModel.loadAnalytics()
            }
        }
    }
}

struct AnalyticsSectionCard<Content: View>: View {
    let title: String
    let icon: String
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Label(title, systemImage: icon)
                .font(.headline)

            content
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
    }
}

struct AnalyticsStat: View {
    let value: String
    let label: String

    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title3.bold())
            Text(label)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

struct RingChart: View {
    let value: Double
    let label: String
    let color: Color

    var body: some View {
        VStack(spacing: 4) {
            ZStack {
                Circle()
                    .stroke(color.opacity(0.2), lineWidth: 6)

                Circle()
                    .trim(from: 0, to: min(value, 1.0))
                    .stroke(color, style: StrokeStyle(lineWidth: 6, lineCap: .round))
                    .rotationEffect(.degrees(-90))

                Text(String(format: "%.0f%%", value * 100))
                    .font(.caption2.bold())
            }
            .frame(width: 60, height: 60)

            Text(label)
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

struct ContentStatRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            Spacer()
            Text(value)
                .font(.subheadline.bold())
        }
    }
}
