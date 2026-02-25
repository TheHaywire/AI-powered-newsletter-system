import Foundation
import SwiftUI

@MainActor
class AuthService: ObservableObject {
    static let shared = AuthService()

    @Published var isAuthenticated = false
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var currentUser: String?

    private let apiService = APIService.shared

    init() {
        checkExistingAuth()
    }

    private func checkExistingAuth() {
        if let token = UserDefaults.standard.string(forKey: "authToken"), !token.isEmpty {
            isAuthenticated = true
            currentUser = UserDefaults.standard.string(forKey: "currentUser")
        }
    }

    func login(username: String, password: String) async {
        isLoading = true
        errorMessage = nil

        do {
            let response = try await apiService.login(username: username, password: password)
            if response.success {
                isAuthenticated = true
                currentUser = username
                UserDefaults.standard.set(username, forKey: "currentUser")
            } else {
                errorMessage = response.message ?? "Login failed"
            }
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func logout() {
        apiService.logout()
        isAuthenticated = false
        currentUser = nil
        UserDefaults.standard.removeObject(forKey: "currentUser")
    }
}
