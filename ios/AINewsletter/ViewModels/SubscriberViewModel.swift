import Foundation

@MainActor
class SubscriberViewModel: ObservableObject {
    @Published var subscribers: [Subscriber] = []
    @Published var totalCount = 0
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var showAddSheet = false

    private let apiService = APIService.shared

    func loadSubscribers() async {
        isLoading = true
        errorMessage = nil

        do {
            let response = try await apiService.fetchSubscribers()
            subscribers = response.subscribers
            totalCount = response.total
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func addSubscriber(email: String, name: String?) async -> Bool {
        do {
            let response = try await apiService.addSubscriber(email: email, name: name)
            if response.success {
                await loadSubscribers()
                return true
            } else {
                errorMessage = response.message
                return false
            }
        } catch {
            errorMessage = error.localizedDescription
            return false
        }
    }

    func removeSubscriber(id: String) async {
        do {
            try await apiService.removeSubscriber(id: id)
            subscribers.removeAll { $0.id == id }
            totalCount = subscribers.count
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
