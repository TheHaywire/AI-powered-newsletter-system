import Foundation

@MainActor
class DashboardViewModel: ObservableObject {
    @Published var stats: DashboardStats?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let apiService = APIService.shared

    func loadDashboard() async {
        isLoading = true
        errorMessage = nil

        do {
            stats = try await apiService.fetchDashboard()
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}
