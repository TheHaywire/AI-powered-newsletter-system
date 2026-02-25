import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var authService: AuthService
    @StateObject private var viewModel = SettingsViewModel()

    var body: some View {
        NavigationStack {
            Form {
                // Account section
                Section("Account") {
                    if let user = authService.currentUser {
                        HStack {
                            Image(systemName: "person.circle.fill")
                                .font(.title)
                                .foregroundStyle(.accent)
                            VStack(alignment: .leading) {
                                Text(user)
                                    .font(.headline)
                                Text("Logged in")
                                    .font(.caption)
                                    .foregroundStyle(.green)
                            }
                        }
                    }

                    Button("Sign Out", role: .destructive) {
                        authService.logout()
                    }
                }

                // Server configuration
                Section("Server") {
                    HStack {
                        Image(systemName: "server.rack")
                        TextField("Server URL", text: $viewModel.settings.serverURL)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                            .keyboardType(.URL)
                    }
                }

                // Newsletter settings
                Section("Newsletter") {
                    HStack {
                        Image(systemName: "paintbrush")
                        TextField("Default Theme", text: $viewModel.settings.theme)
                    }
                }

                // Notifications
                Section("Notifications") {
                    Toggle(isOn: $viewModel.settings.notificationsEnabled) {
                        Label("Push Notifications", systemImage: "bell")
                    }
                }

                // Auto-refresh
                Section("Data") {
                    Toggle(isOn: $viewModel.settings.autoRefresh) {
                        Label("Auto Refresh", systemImage: "arrow.clockwise")
                    }

                    if viewModel.settings.autoRefresh {
                        Stepper(
                            value: $viewModel.settings.refreshIntervalMinutes,
                            in: 5...120,
                            step: 5
                        ) {
                            Label(
                                "Every \(viewModel.settings.refreshIntervalMinutes) min",
                                systemImage: "timer"
                            )
                        }
                    }
                }

                // Actions
                Section {
                    Button("Save Settings") {
                        viewModel.saveSettings()
                    }

                    Button("Reset to Defaults") {
                        viewModel.resetToDefaults()
                    }
                    .foregroundStyle(.orange)
                }

                if let status = viewModel.statusMessage {
                    Section {
                        Label(status, systemImage: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                    }
                }

                // About
                Section("About") {
                    HStack {
                        Text("Version")
                        Spacer()
                        Text("1.0.0")
                            .foregroundStyle(.secondary)
                    }

                    HStack {
                        Text("Platform")
                        Spacer()
                        Text("iOS")
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Settings")
        }
    }
}
