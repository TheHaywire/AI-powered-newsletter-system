import SwiftUI

struct GenerateView: View {
    @StateObject private var viewModel = GenerateViewModel()

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Header illustration
                    VStack(spacing: 12) {
                        Image(systemName: "sparkles")
                            .font(.system(size: 48))
                            .foregroundStyle(.accent)

                        Text("Generate Newsletter")
                            .font(.title2.bold())

                        Text("AI will research trending topics, analyze articles, and create a professional newsletter.")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                    .padding(.top, 20)

                    // Theme input
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Theme")
                            .font(.headline)

                        TextField("Enter newsletter theme...", text: $viewModel.theme)
                            .textFieldStyle(.roundedBorder)

                        Text("Choose a topic focus for your newsletter")
                            .font(.caption)
                            .foregroundStyle(.tertiary)
                    }
                    .padding(.horizontal)

                    // Suggested themes
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Suggested Themes")
                            .font(.subheadline.bold())
                            .foregroundStyle(.secondary)
                            .padding(.horizontal)

                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 8) {
                                ForEach(viewModel.suggestedThemes, id: \.self) { theme in
                                    Button {
                                        viewModel.theme = theme
                                    } label: {
                                        Text(theme)
                                            .font(.caption)
                                            .padding(.horizontal, 12)
                                            .padding(.vertical, 8)
                                            .background(
                                                viewModel.theme == theme
                                                    ? Color.accentColor.opacity(0.2)
                                                    : Color(.systemGray6)
                                            )
                                            .foregroundStyle(
                                                viewModel.theme == theme
                                                    ? .accent
                                                    : .primary
                                            )
                                            .clipShape(Capsule())
                                    }
                                }
                            }
                            .padding(.horizontal)
                        }
                    }

                    // Generate button
                    Button {
                        Task { await viewModel.generate() }
                    } label: {
                        Group {
                            if viewModel.isGenerating {
                                HStack(spacing: 8) {
                                    ProgressView()
                                        .tint(.white)
                                    Text("Generating...")
                                }
                            } else {
                                Label("Generate Newsletter", systemImage: "sparkles")
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(viewModel.theme.isEmpty || viewModel.isGenerating)
                    .padding(.horizontal)

                    // Error message
                    if let error = viewModel.errorMessage {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundStyle(.red)
                            Text(error)
                                .font(.caption)
                                .foregroundStyle(.red)
                        }
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.red.opacity(0.1), in: RoundedRectangle(cornerRadius: 10))
                        .padding(.horizontal)
                    }

                    // Success result
                    if let result = viewModel.result {
                        VStack(spacing: 12) {
                            Image(systemName: result.success ? "checkmark.circle.fill" : "xmark.circle.fill")
                                .font(.title)
                                .foregroundStyle(result.success ? .green : .red)

                            Text(result.message)
                                .font(.subheadline)
                                .multilineTextAlignment(.center)

                            if let id = result.newsletterId {
                                NavigationLink(value: id) {
                                    Label("View Newsletter", systemImage: "newspaper")
                                }
                                .buttonStyle(.bordered)
                            }
                        }
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
                        .padding(.horizontal)
                    }

                    // Pipeline info
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Generation Pipeline")
                            .font(.subheadline.bold())
                            .foregroundStyle(.secondary)

                        PipelineStep(number: 1, title: "Research", description: "Discover trending topics & collect articles", icon: "magnifyingglass")
                        PipelineStep(number: 2, title: "Analysis", description: "Sentiment, relevance & bias analysis", icon: "chart.bar")
                        PipelineStep(number: 3, title: "Creation", description: "AI-powered content generation", icon: "text.badge.star")
                        PipelineStep(number: 4, title: "Quality Check", description: "Validate quality thresholds", icon: "checkmark.shield")
                    }
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
                    .padding(.horizontal)

                    Spacer().frame(height: 20)
                }
            }
            .navigationTitle("Generate")
            .navigationDestination(for: String.self) { id in
                NewsletterDetailView(newsletterId: id)
            }
        }
    }
}

struct PipelineStep: View {
    let number: Int
    let title: String
    let description: String
    let icon: String

    var body: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(.accent.opacity(0.15))
                    .frame(width: 36, height: 36)
                Image(systemName: icon)
                    .font(.caption)
                    .foregroundStyle(.accent)
            }

            VStack(alignment: .leading, spacing: 2) {
                Text("\(number). \(title)")
                    .font(.subheadline.bold())
                Text(description)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }
}
