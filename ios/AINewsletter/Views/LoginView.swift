import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authService: AuthService
    @State private var username = ""
    @State private var password = ""

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 32) {
                    Spacer().frame(height: 40)

                    // App icon and title
                    VStack(spacing: 12) {
                        Image(systemName: "newspaper.fill")
                            .font(.system(size: 64))
                            .foregroundStyle(.accent)

                        Text("AI Newsletter")
                            .font(.largeTitle.bold())

                        Text("Your AI-powered newsletter platform")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }

                    // Login form
                    VStack(spacing: 16) {
                        TextField("Username", text: $username)
                            .textFieldStyle(.roundedBorder)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()

                        SecureField("Password", text: $password)
                            .textFieldStyle(.roundedBorder)

                        if let error = authService.errorMessage {
                            Text(error)
                                .font(.caption)
                                .foregroundStyle(.red)
                                .multilineTextAlignment(.center)
                        }

                        Button {
                            Task {
                                await authService.login(username: username, password: password)
                            }
                        } label: {
                            Group {
                                if authService.isLoading {
                                    ProgressView()
                                        .tint(.white)
                                } else {
                                    Text("Sign In")
                                }
                            }
                            .frame(maxWidth: .infinity)
                            .frame(height: 44)
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(username.isEmpty || password.isEmpty || authService.isLoading)
                    }
                    .padding(.horizontal, 32)

                    // Server config hint
                    VStack(spacing: 4) {
                        Text("Configure your server in Settings after login")
                            .font(.caption)
                            .foregroundStyle(.tertiary)
                    }
                }
                .padding()
            }
        }
    }
}
