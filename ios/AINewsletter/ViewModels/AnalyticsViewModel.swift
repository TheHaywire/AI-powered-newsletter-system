import Foundation

@MainActor
class AnalyticsViewModel: ObservableObject {
    @Published var analytics: AnalyticsData?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let apiService = APIService.shared

    func loadAnalytics() async {
        isLoading = true
        errorMessage = nil

        do {
            analytics = try await apiService.fetchAnalytics()
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}
