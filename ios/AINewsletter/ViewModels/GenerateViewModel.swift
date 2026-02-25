import Foundation

@MainActor
class GenerateViewModel: ObservableObject {
    @Published var theme = ""
    @Published var isGenerating = false
    @Published var result: GenerationResponse?
    @Published var errorMessage: String?

    let suggestedThemes = [
        "Technology & AI",
        "Business & Startups",
        "Science & Innovation",
        "Blockchain & Web3",
        "Climate & Sustainability",
        "Health & Biotech"
    ]

    private let apiService = APIService.shared

    func generate() async {
        guard !theme.trimmingCharacters(in: .whitespaces).isEmpty else {
            errorMessage = "Please enter a theme"
            return
        }

        isGenerating = true
        errorMessage = nil
        result = nil

        do {
            result = try await apiService.generateNewsletter(theme: theme)
        } catch {
            errorMessage = error.localizedDescription
        }

        isGenerating = false
    }
}
