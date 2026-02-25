import SwiftUI

struct NewsletterListView: View {
    @StateObject private var viewModel = NewsletterViewModel()
    @State private var searchText = ""

    var filteredNewsletters: [Newsletter] {
        if searchText.isEmpty {
            return viewModel.newsletters
        }
        return viewModel.newsletters.filter { newsletter in
            newsletter.title.localizedCaseInsensitiveContains(searchText) ||
            (newsletter.theme?.localizedCaseInsensitiveContains(searchText) ?? false)
        }
    }

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading && viewModel.newsletters.isEmpty {
                    ProgressView("Loading newsletters...")
                        .frame(maxWidth: .infinity, minHeight: 300)
                } else if let error = viewModel.errorMessage, viewModel.newsletters.isEmpty {
                    ContentUnavailableView {
                        Label("Error", systemImage: "exclamationmark.triangle")
                    } description: {
                        Text(error)
                    } actions: {
                        Button("Retry") {
                            Task { await viewModel.loadNewsletters() }
                        }
                    }
                } else if viewModel.newsletters.isEmpty {
                    ContentUnavailableView(
                        "No Newsletters",
                        systemImage: "newspaper",
                        description: Text("Generate your first newsletter to get started")
                    )
                } else {
                    List {
                        ForEach(filteredNewsletters) { newsletter in
                            NavigationLink(value: newsletter.id) {
                                NewsletterRow(newsletter: newsletter)
                            }
                        }
                        .onDelete { indexSet in
                            Task {
                                for index in indexSet {
                                    let newsletter = filteredNewsletters[index]
                                    await viewModel.deleteNewsletter(id: newsletter.id)
                                }
                            }
                        }
                    }
                    .searchable(text: $searchText, prompt: "Search newsletters")
                }
            }
            .navigationTitle("Newsletters")
            .refreshable {
                await viewModel.loadNewsletters()
            }
            .navigationDestination(for: String.self) { id in
                NewsletterDetailView(newsletterId: id)
            }
            .task {
                await viewModel.loadNewsletters()
            }
        }
    }
}

struct NewsletterRow: View {
    let newsletter: Newsletter

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(newsletter.title)
                    .font(.headline)
                    .lineLimit(2)

                Spacer()

                if let status = newsletter.status {
                    StatusBadge(status: status)
                }
            }

            if let subtitle = newsletter.subtitle {
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }

            HStack(spacing: 12) {
                if let theme = newsletter.theme {
                    Label(theme, systemImage: "tag")
                        .font(.caption)
                        .foregroundStyle(.accent)
                }

                if let metrics = newsletter.metrics {
                    Label("\(metrics.articleCount) articles", systemImage: "doc.text")
                        .font(.caption)
                        .foregroundStyle(.secondary)

                    Label("\(metrics.readingTimeMinutes) min", systemImage: "clock")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

struct StatusBadge: View {
    let status: String

    var color: Color {
        switch status.lowercased() {
        case "published", "sent": return .green
        case "draft": return .orange
        case "generating": return .blue
        case "failed": return .red
        default: return .gray
        }
    }

    var body: some View {
        Text(status.capitalized)
            .font(.caption2.bold())
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(color.opacity(0.15), in: Capsule())
            .foregroundStyle(color)
    }
}
