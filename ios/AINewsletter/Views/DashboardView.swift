import SwiftUI

struct DashboardView: View {
    @StateObject private var viewModel = DashboardViewModel()

    var body: some View {
        NavigationStack {
            ScrollView {
                if viewModel.isLoading && viewModel.stats == nil {
                    ProgressView("Loading dashboard...")
                        .frame(maxWidth: .infinity, minHeight: 300)
                } else if let error = viewModel.errorMessage, viewModel.stats == nil {
                    ContentUnavailableView {
                        Label("Connection Error", systemImage: "wifi.slash")
                    } description: {
                        Text(error)
                    } actions: {
                        Button("Retry") {
                            Task { await viewModel.loadDashboard() }
                        }
                    }
                } else if let stats = viewModel.stats {
                    VStack(spacing: 20) {
                        // Stats grid
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 16) {
                            StatCard(
                                title: "Newsletters",
                                value: "\(stats.totalNewsletters)",
                                icon: "newspaper",
                                color: .blue
                            )
                            StatCard(
                                title: "Subscribers",
                                value: "\(stats.totalSubscribers)",
                                icon: "person.2",
                                color: .green
                            )
                            StatCard(
                                title: "Articles",
                                value: "\(stats.totalArticles)",
                                icon: "doc.text",
                                color: .orange
                            )
                            StatCard(
                                title: "Delivery Rate",
                                value: String(format: "%.0f%%", stats.deliveryRate * 100),
                                icon: "paperplane",
                                color: .purple
                            )
                        }
                        .padding(.horizontal)

                        // Recent newsletters
                        if !stats.recentNewsletters.isEmpty {
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Recent Newsletters")
                                    .font(.headline)
                                    .padding(.horizontal)

                                ForEach(stats.recentNewsletters) { newsletter in
                                    NavigationLink(value: newsletter.id) {
                                        RecentNewsletterRow(newsletter: newsletter)
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }
                    }
                    .padding(.vertical)
                } else {
                    ContentUnavailableView(
                        "No Data",
                        systemImage: "chart.bar.doc.horizontal",
                        description: Text("Pull to refresh or check your connection")
                    )
                }
            }
            .navigationTitle("Dashboard")
            .refreshable {
                await viewModel.loadDashboard()
            }
            .navigationDestination(for: String.self) { id in
                NewsletterDetailView(newsletterId: id)
            }
            .task {
                await viewModel.loadDashboard()
            }
        }
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundStyle(color)

            Text(value)
                .font(.title.bold())

            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }
}

struct RecentNewsletterRow: View {
    let newsletter: Newsletter

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(newsletter.title)
                    .font(.subheadline.bold())
                    .lineLimit(1)

                if let theme = newsletter.theme {
                    Text(theme)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Spacer()

            if let metrics = newsletter.metrics {
                VStack(alignment: .trailing, spacing: 2) {
                    Text("\(metrics.articleCount) articles")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                    Text("\(metrics.readingTimeMinutes) min read")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }

            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundStyle(.tertiary)
        }
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 10))
        .padding(.horizontal)
    }
}
