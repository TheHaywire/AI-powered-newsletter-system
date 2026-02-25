import Foundation

@MainActor
class SettingsViewModel: ObservableObject {
    @Published var settings: AppSettings
    @Published var isSaving = false
    @Published var statusMessage: String?

    private let apiService = APIService.shared

    init() {
        if let data = UserDefaults.standard.data(forKey: "appSettings"),
           let saved = try? JSONDecoder().decode(AppSettings.self, from: data) {
            self.settings = saved
        } else {
            self.settings = .default
        }
    }

    func saveSettings() {
        isSaving = true
        apiService.baseURL = settings.serverURL

        if let data = try? JSONEncoder().encode(settings) {
            UserDefaults.standard.set(data, forKey: "appSettings")
        }

        statusMessage = "Settings saved"
        isSaving = false

        Task {
            try? await Task.sleep(nanoseconds: 2_000_000_000)
            statusMessage = nil
        }
    }

    func resetToDefaults() {
        settings = .default
        saveSettings()
    }
}
