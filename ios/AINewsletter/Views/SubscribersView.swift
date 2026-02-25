import SwiftUI

struct SubscribersView: View {
    @StateObject private var viewModel = SubscriberViewModel()

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading && viewModel.subscribers.isEmpty {
                    ProgressView("Loading subscribers...")
                        .frame(maxWidth: .infinity, minHeight: 300)
                } else if let error = viewModel.errorMessage, viewModel.subscribers.isEmpty {
                    ContentUnavailableView {
                        Label("Error", systemImage: "exclamationmark.triangle")
                    } description: {
                        Text(error)
                    } actions: {
                        Button("Retry") {
                            Task { await viewModel.loadSubscribers() }
                        }
                    }
                } else if viewModel.subscribers.isEmpty {
                    ContentUnavailableView(
                        "No Subscribers",
                        systemImage: "person.2",
                        description: Text("Add subscribers to start sending newsletters")
                    )
                } else {
                    List {
                        Section {
                            HStack {
                                Label("Total Subscribers", systemImage: "person.2.fill")
                                Spacer()
                                Text("\(viewModel.totalCount)")
                                    .font(.headline)
                                    .foregroundStyle(.accent)
                            }

                            HStack {
                                Label("Active", systemImage: "checkmark.circle.fill")
                                Spacer()
                                let activeCount = viewModel.subscribers.filter(\.isActive).count
                                Text("\(activeCount)")
                                    .foregroundStyle(.green)
                            }
                        }

                        Section("Subscribers") {
                            ForEach(viewModel.subscribers) { subscriber in
                                SubscriberRow(subscriber: subscriber)
                            }
                            .onDelete { indexSet in
                                Task {
                                    for index in indexSet {
                                        let sub = viewModel.subscribers[index]
                                        await viewModel.removeSubscriber(id: sub.id)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Subscribers")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button {
                        viewModel.showAddSheet = true
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $viewModel.showAddSheet) {
                AddSubscriberSheet(viewModel: viewModel)
            }
            .refreshable {
                await viewModel.loadSubscribers()
            }
            .task {
                await viewModel.loadSubscribers()
            }
        }
    }
}

struct SubscriberRow: View {
    let subscriber: Subscriber

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(subscriber.name ?? subscriber.email)
                    .font(.subheadline.bold())

                if subscriber.name != nil {
                    Text(subscriber.email)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                if let prefs = subscriber.preferences, let cats = prefs.categories, !cats.isEmpty {
                    Text(cats.joined(separator: ", "))
                        .font(.caption2)
                        .foregroundStyle(.accent)
                }
            }

            Spacer()

            Circle()
                .fill(subscriber.isActive ? .green : .gray)
                .frame(width: 8, height: 8)
        }
    }
}

struct AddSubscriberSheet: View {
    @ObservedObject var viewModel: SubscriberViewModel
    @Environment(\.dismiss) var dismiss
    @State private var email = ""
    @State private var name = ""
    @State private var isSubmitting = false

    var body: some View {
        NavigationStack {
            Form {
                Section("Contact Info") {
                    TextField("Email", text: $email)
                        .textInputAutocapitalization(.never)
                        .keyboardType(.emailAddress)
                        .autocorrectionDisabled()

                    TextField("Name (optional)", text: $name)
                }

                if let error = viewModel.errorMessage {
                    Section {
                        Text(error)
                            .foregroundStyle(.red)
                            .font(.caption)
                    }
                }
            }
            .navigationTitle("Add Subscriber")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Add") {
                        isSubmitting = true
                        Task {
                            let success = await viewModel.addSubscriber(
                                email: email,
                                name: name.isEmpty ? nil : name
                            )
                            isSubmitting = false
                            if success { dismiss() }
                        }
                    }
                    .disabled(email.isEmpty || isSubmitting)
                }
            }
        }
    }
}
