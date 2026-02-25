import SwiftUI

@main
struct AINewsletterApp: App {
    @StateObject private var authService = AuthService.shared
    @StateObject private var apiService = APIService.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authService)
                .environmentObject(apiService)
        }
    }
}
