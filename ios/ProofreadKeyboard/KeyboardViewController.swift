import UIKit

/// Synthetic, offline feasibility harness. No networking, shared containers,
/// credentials, conversation history, or host-text persistence.
final class KeyboardViewController: UIInputViewController {
    private let model = KeyboardPrototypeModel()
    private let rootStack = UIStackView()
    private let typingStack = UIStackView()
    private let panelScrollView = UIScrollView()
    private let panelStack = UIStackView()
    private let suggestionStack = UIStackView()
    private let proofreadButton = UIButton(type: .system)
    private let nextKeyboardButton = UIButton(type: .system)
    private let fullAccessLabel = UILabel()
    private let contextSummaryLabel = UILabel()
    private let modeControl = UISegmentedControl(items: ["Generate", "Rewrite"])
    private var keyboardHeight: NSLayoutConstraint?
    private var panelVisible = false

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        configureLayout()
        updateFullAccessLabel()
        clearSuggestions()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        updateFullAccessLabel()
        clearSuggestions()
    }

    override func viewWillDisappear(_ animated: Bool) {
        clearSuggestions()
        super.viewWillDisappear(animated)
    }

    override func viewWillTransition(to size: CGSize, with coordinator: UIViewControllerTransitionCoordinator) {
        clearSuggestions()
        super.viewWillTransition(to: size, with: coordinator)
    }

    override func viewWillLayoutSubviews() {
        super.viewWillLayoutSubviews()
        nextKeyboardButton.isHidden = !needsInputModeSwitchKey
    }

    override func textDidChange(_ textInput: UITextInput?) {
        super.textDidChange(textInput)
        clearSuggestions()
        updateFullAccessLabel()
    }

    override func selectionDidChange(_ textInput: UITextInput?) {
        super.selectionDidChange(textInput)
        clearSuggestions()
    }

    private func configureLayout() {
        rootStack.axis = .vertical
        rootStack.spacing = 6
        rootStack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(rootStack)
        NSLayoutConstraint.activate([
            rootStack.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 8),
            rootStack.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor, constant: -8),
            rootStack.topAnchor.constraint(equalTo: view.topAnchor, constant: 8),
            rootStack.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -8)
        ])
        let height = view.heightAnchor.constraint(equalToConstant: 300)
        height.priority = UILayoutPriority(rawValue: 999)
        height.isActive = true
        keyboardHeight = height

        configureButton(proofreadButton, title: "Proofread · offline prototype")
        proofreadButton.addAction(UIAction { [weak self] _ in self?.togglePanel() }, for: .touchUpInside)
        rootStack.addArrangedSubview(proofreadButton)

        fullAccessLabel.font = .preferredFont(forTextStyle: .caption1)
        fullAccessLabel.adjustsFontForContentSizeCategory = true
        fullAccessLabel.numberOfLines = 2
        fullAccessLabel.textAlignment = .center
        rootStack.addArrangedSubview(fullAccessLabel)

        typingStack.axis = .vertical
        typingStack.spacing = 6
        for letters in ["qwertyuiop", "asdfghjkl", "zxcvbnm"] {
            let row = UIStackView()
            row.spacing = 4
            row.distribution = .fillEqually
            for letter in letters {
                let text = String(letter)
                row.addArrangedSubview(button(text) { [weak self] in self?.type(text) })
            }
            typingStack.addArrangedSubview(row)
        }
        rootStack.addArrangedSubview(typingStack)

        configurePanel()
        rootStack.addArrangedSubview(panelScrollView)
        panelScrollView.isHidden = true

        let actions = UIStackView()
        actions.spacing = 4
        actions.distribution = .fillEqually
        configureButton(nextKeyboardButton, title: "🌐")
        nextKeyboardButton.accessibilityLabel = "Next keyboard"
        nextKeyboardButton.addTarget(self, action: #selector(handleInputModeList(from:with:)), for: .allTouchEvents)
        actions.addArrangedSubview(nextKeyboardButton)
        actions.addArrangedSubview(button("Space") { [weak self] in self?.type(" ") })
        actions.addArrangedSubview(button("Delete") { [weak self] in
            self?.clearSuggestions()
            self?.textDocumentProxy.deleteBackward()
        })
        actions.addArrangedSubview(button("Return") { [weak self] in self?.type("\n") })
        rootStack.addArrangedSubview(actions)
    }

    private func configurePanel() {
        panelScrollView.heightAnchor.constraint(equalToConstant: 230).isActive = true
        panelStack.axis = .vertical
        panelStack.spacing = 8
        panelStack.translatesAutoresizingMaskIntoConstraints = false
        panelScrollView.addSubview(panelStack)
        NSLayoutConstraint.activate([
            panelStack.leadingAnchor.constraint(equalTo: panelScrollView.contentLayoutGuide.leadingAnchor),
            panelStack.trailingAnchor.constraint(equalTo: panelScrollView.contentLayoutGuide.trailingAnchor),
            panelStack.topAnchor.constraint(equalTo: panelScrollView.contentLayoutGuide.topAnchor),
            panelStack.bottomAnchor.constraint(equalTo: panelScrollView.contentLayoutGuide.bottomAnchor),
            panelStack.widthAnchor.constraint(equalTo: panelScrollView.frameLayoutGuide.widthAnchor)
        ])

        let disclosure = UILabel()
        disclosure.font = .preferredFont(forTextStyle: .caption1)
        disclosure.adjustsFontForContentSizeCategory = true
        disclosure.numberOfLines = 0
        disclosure.text = "Fixed offline examples · not personalized. Your text is not used to generate these examples. This keyboard cannot read the conversation above the field."
        panelStack.addArrangedSubview(disclosure)

        modeControl.selectedSegmentIndex = 0
        modeControl.addAction(UIAction { [weak self] _ in self?.clearSuggestions() }, for: .valueChanged)
        panelStack.addArrangedSubview(modeControl)
        panelStack.addArrangedSubview(button("Capture available context · show examples") { [weak self] in
            self?.captureExamples()
        })

        contextSummaryLabel.font = .preferredFont(forTextStyle: .caption1)
        contextSummaryLabel.adjustsFontForContentSizeCategory = true
        contextSummaryLabel.numberOfLines = 0
        panelStack.addArrangedSubview(contextSummaryLabel)
        suggestionStack.axis = .vertical
        suggestionStack.spacing = 8
        panelStack.addArrangedSubview(suggestionStack)
    }

    private func togglePanel() {
        clearSuggestions()
        panelVisible.toggle()
        typingStack.isHidden = panelVisible
        panelScrollView.isHidden = !panelVisible
        keyboardHeight?.constant = panelVisible ? 380 : 300
        proofreadButton.setTitle(panelVisible ? "Back to typing" : "Proofread · offline prototype", for: .normal)
    }

    private func type(_ text: String) {
        clearSuggestions()
        textDocumentProxy.insertText(text)
    }

    /// Proxy text is read only after explicit capture or to recheck an insertion.
    /// It may be partial/unavailable and cannot establish the full document state.
    private func snapshot() -> KeyboardContextSnapshot {
        KeyboardContextSnapshot(
            before: textDocumentProxy.documentContextBeforeInput,
            after: textDocumentProxy.documentContextAfterInput,
            selection: textDocumentProxy.selectedText,
            documentIdentifier: textDocumentProxy.documentIdentifier
        )
    }

    private func captureExamples() {
        let context = snapshot()
        model.capture(context, mode: modeControl.selectedSegmentIndex == 0 ? .generate : .rewrite)
        updateFullAccessLabel()
        renderSuggestions()
        let summary = "Available scalars — before: \(countSummary(context.before)); after: \(countSummary(context.after)); selection: \(countSummary(context.selection))."
        contextSummaryLabel.text = model.candidates.isEmpty
            ? summary + " Context is unavailable, selected, or too large. No insertion is enabled."
            : summary + " Limited proxy snapshot only. Choose an example to insert at the cursor; nothing is sent."
    }

    private func insertCandidate(_ id: Int) {
        guard let text = model.takeCandidate(id, currentContext: snapshot()) else {
            renderSuggestions()
            contextSummaryLabel.text = "The available context changed or insertion is unsafe. Capture again."
            return
        }
        renderSuggestions()
        textDocumentProxy.insertText(text)
        contextSummaryLabel.text = "Example inserted at the cursor. Edit it in the host field; nothing was sent."
    }

    private func clearSuggestions() {
        model.invalidate()
        renderSuggestions()
        contextSummaryLabel.text = "Capture explicitly to inspect a limited context summary. No host text is displayed or saved to disk."
    }

    private func renderSuggestions() {
        for child in suggestionStack.arrangedSubviews {
            suggestionStack.removeArrangedSubview(child)
            child.removeFromSuperview()
        }
        for candidate in model.candidates {
            let id = candidate.id
            suggestionStack.addArrangedSubview(button("Insert example: \(candidate.text)") { [weak self] in
                self?.insertCandidate(id)
            })
        }
    }

    private func updateFullAccessLabel() {
        fullAccessLabel.text = "Full Access: \(hasFullAccess ? "on" : "off") · This prototype stays offline."
    }

    private func countSummary(_ text: String?) -> String {
        guard let text else { return "unavailable" }
        let count = text.unicodeScalars.prefix(1_001).count
        return count > 1_000 ? "more than 1,000" : String(count)
    }

    private func button(_ title: String, action: @escaping () -> Void) -> UIButton {
        let result = UIButton(type: .system)
        configureButton(result, title: title)
        result.addAction(UIAction { _ in action() }, for: .touchUpInside)
        return result
    }

    private func configureButton(_ button: UIButton, title: String) {
        button.setTitle(title, for: .normal)
        button.backgroundColor = .secondarySystemFill
        button.layer.cornerRadius = 6
        button.titleLabel?.font = .preferredFont(forTextStyle: .callout)
        button.titleLabel?.adjustsFontForContentSizeCategory = true
        button.titleLabel?.numberOfLines = 0
        button.heightAnchor.constraint(greaterThanOrEqualToConstant: 40).isActive = true
    }
}
