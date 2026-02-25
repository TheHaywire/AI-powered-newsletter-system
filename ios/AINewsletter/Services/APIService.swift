import Foundation

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(statusCode: Int, message: String?)
    case decodingError(Error)
    case networkError(Error)
    case unauthorized

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid server response"
        case .httpError(let code, let message):
            return message ?? "HTTP error \(code)"
        case .decodingError(let error):
            return "Failed to parse response: \(error.localizedDescription)"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .unauthorized:
            return "Authentication required. Please log in."
        }
    }
}

@MainActor
class APIService: ObservableObject {
    static let shared = APIService()

    @Published var baseURL: String {
        didSet {
            UserDefaults.standard.set(baseURL, forKey: "serverURL")
        }
    }

    private let session: URLSession
    private let decoder: JSONDecoder

    init() {
        self.baseURL = UserDefaults.standard.string(forKey: "serverURL") ?? "http://localhost:5000"

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 120
        self.session = URLSession(configuration: config)

        self.decoder = JSONDecoder()
        self.decoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let dateString = try container.decode(String.self)

            let formatters = [
                APIService.iso8601Formatter,
                APIService.simpleDateFormatter
            ]

            for formatter in formatters {
                if let date = formatter.date(from: dateString) {
                    return date
                }
            }

            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Cannot decode date: \(dateString)"
            )
        }
    }

    private static let iso8601Formatter: ISO8601DateFormatter = {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return f
    }()

    private static let simpleDateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm:ss"
        f.locale = Locale(identifier: "en_US_POSIX")
        return f
    }()

    private var authToken: String? {
        UserDefaults.standard.string(forKey: "authToken")
    }

    private func makeRequest(path: String, method: String = "GET", body: Data? = nil) throws -> URLRequest {
        guard let url = URL(string: "\(baseURL)\(path)") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = body
        }

        return request
    }

    private func perform<T: Decodable>(_ request: URLRequest) async throws -> T {
        let data: Data
        let response: URLResponse

        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw APIError.networkError(error)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        if httpResponse.statusCode == 401 {
            throw APIError.unauthorized
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            let message = String(data: data, encoding: .utf8)
            throw APIError.httpError(statusCode: httpResponse.statusCode, message: message)
        }

        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingError(error)
        }
    }

    // MARK: - Dashboard

    func fetchDashboard() async throws -> DashboardStats {
        let request = try makeRequest(path: "/api/dashboard")
        return try await perform(request)
    }

    // MARK: - Newsletters

    func fetchNewsletters() async throws -> [Newsletter] {
        let request = try makeRequest(path: "/api/newsletters")
        return try await perform(request)
    }

    func fetchNewsletter(id: String) async throws -> Newsletter {
        let request = try makeRequest(path: "/api/newsletters/\(id)")
        return try await perform(request)
    }

    func generateNewsletter(theme: String) async throws -> GenerationResponse {
        let body = try JSONEncoder().encode(GenerationRequest(theme: theme))
        let request = try makeRequest(path: "/api/generate", method: "POST", body: body)
        return try await perform(request)
    }

    func deleteNewsletter(id: String) async throws {
        let request = try makeRequest(path: "/api/newsletters/\(id)", method: "DELETE")
        let _: GenerationResponse = try await perform(request)
    }

    // MARK: - Subscribers

    func fetchSubscribers() async throws -> SubscriberListResponse {
        let request = try makeRequest(path: "/api/subscribers")
        return try await perform(request)
    }

    func addSubscriber(email: String, name: String?) async throws -> SubscriberResponse {
        let body = try JSONEncoder().encode(AddSubscriberRequest(email: email, name: name))
        let request = try makeRequest(path: "/api/subscribers", method: "POST", body: body)
        return try await perform(request)
    }

    func removeSubscriber(id: String) async throws {
        let request = try makeRequest(path: "/api/subscribers/\(id)", method: "DELETE")
        let _: SubscriberResponse = try await perform(request)
    }

    // MARK: - Analytics

    func fetchAnalytics() async throws -> AnalyticsData {
        let request = try makeRequest(path: "/api/analytics")
        return try await perform(request)
    }

    // MARK: - Authentication

    func login(username: String, password: String) async throws -> LoginResponse {
        let body = try JSONEncoder().encode(LoginRequest(username: username, password: password))
        let request = try makeRequest(path: "/api/login", method: "POST", body: body)
        let response: LoginResponse = try await perform(request)

        if response.success, let token = response.token {
            UserDefaults.standard.set(token, forKey: "authToken")
        }

        return response
    }

    func logout() {
        UserDefaults.standard.removeObject(forKey: "authToken")
    }
}

struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct LoginResponse: Codable {
    let success: Bool
    let message: String?
    let token: String?
}
