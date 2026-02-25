import Foundation

@MainActor
class NewsletterViewModel: ObservableObject {
    @Published var newsletters: [Newsletter] = []
    @Published var selectedNewsletter: Newsletter?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let apiService = APIService.shared

    func loadNewsletters() async {
        isLoading = true
        errorMessage = nil

        do {
            newsletters = try await apiService.fetchNewsletters()
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func loadNewsletter(id: String) async {
        isLoading = true
        errorMessage = nil

        do {
            selectedNewsletter = try await apiService.fetchNewsletter(id: id)
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func deleteNewsletter(id: String) async {
        do {
            try await apiService.deleteNewsletter(id: id)
            newsletters.removeAll { $0.id == id }
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
