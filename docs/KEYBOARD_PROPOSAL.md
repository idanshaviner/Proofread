# Proofread cross-application keyboard proposal

Status: **narrow synthetic feasibility spike approved October 30, 2026**.
The owner approved the final question authorizing this spike. Full product UI,
personalization, network/private-data integration and release remain proposals.
See `KEYBOARD_PROTOTYPE_TESTING.md` for implementation scope and unrun native gates.
Owner source: [keyboard requirement](source/KEYBOARD_REQUIREMENT_2026-10-30.md).
This supersedes earlier provisional documents that deferred keyboards indefinitely.
It establishes product direction, not authorization for extension UX, entitlements,
private-data policy, new spending or release. Offline prototype source is now
implemented; the architecture-gap descriptions below document the pre-spike
baseline. Current source scope and unrun native gates are in the testing guide.

## Feasibility and essential product distinction

A supported custom iOS keyboard can offer Proofread assistance within compatible
apps and insert user-selected text into the active editable field. It cannot add
our button to Apple's existing keyboard, control Apple's microphone/globe area,
read another app's chat transcript, or promise universal application compatibility.
The user must enable/select the Proofread keyboard using iOS keyboard settings
and switching controls. This distinction needs explicit owner acceptance before
building the proposed experience.

The recommendation is a lightweight `UIInputViewController` extension with our
own Proofread toolbar button and assistance panel, backed by the same generation
engine as the containing application. The standalone app remains the voluntary
place for onboarding, permission explanations, profile/relationship management,
authentication and deletion. It is not required for every generation once setup
is complete. Do not build a second model pipeline for the extension.

## Evidence and source limitations

Official Apple reads attempted October 30 returned proxy CONNECT 403: archived
Custom Keyboard guide, App Review Guidelines, current UITextDocumentProxy and
hasFullAccess reference JSON, and App Groups extension scenarios. The references
below are authoritative locations, **not successfully refreshed evidence**. The
constraints in this proposal reflect established SDK behavior; check current
Apple documentation/SDK and App Review text on an accessible Mac/network before
implementation acceptance. No application compatibility or device test ran here.

- [Apple Custom Keyboard guide](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/CustomKeyboard.html)
- [UIInputViewController](https://developer.apple.com/documentation/uikit/uiinputviewcontroller)
- [UITextDocumentProxy](https://developer.apple.com/documentation/uikit/uitextdocumentproxy)
- [hasFullAccess](https://developer.apple.com/documentation/uikit/uiinputviewcontroller/hasfullaccess)
- [Extension shared scenarios / App Groups](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/ExtensionScenarios.html)
- [App Review Guidelines, extension/keyboard rules](https://developer.apple.com/app-store/review/guidelines/)

## Platform capabilities and boundaries

| Requirement | Supported direction | Constraint / acceptance check |
| --- | --- | --- |
| Button beside Apple's dictation control | Not supported for a third-party app | Place a button inside OUR keyboard toolbar. Host-specific accessory bars cannot be installed across unrelated apps. |
| Standard editable fields | Custom keyboard extension | Host may reject third-party keyboards. Test each app/version and field. |
| Secure/password input | System keyboard normally replaces third-party keyboard | Never work around secure-input restrictions or capture passwords. |
| Phone/name-phone pads | System keyboard behavior restricts custom keyboards | Test exact input types; do not promise all numeric/search controls behave alike. |
| Search fields | Often standard editable fields | Field type, custom host input and host opt-out determine behavior; not universal. |
| Draft before/after cursor and selected text | `textDocumentProxy` context/selection when provided | Context may be nil, truncated or change between calls; no fixed guaranteed window. |
| Incoming messages / full conversation | Not exposed by keyboard APIs | Never infer a transcript from the composing field. User explicitly supplies minimal context when needed. |
| Insert chosen candidate | `textDocumentProxy.insertText` | Insert at active cursor/selection. No auto-send or programmatic access to host send button. |
| Replace draft | Proxy deletion/insertion, limited scope | Broad replacement is risky when context is partial or changes. Prototype inserts by default; selection-based replacement requires approved UX and host tests. |
| Hosted AI networking | Extension networking with requested/granted Full Access | Check `hasFullAccess` and connectivity before calls. Disabled/denied state must remain usable for ordinary keyboard input. |
| Shared configuration/profile references | App Group plus approved sharing policy | Shared container is not arbitrary access to the main app sandbox or a substitute for consent/encryption. Check current Full Access container restrictions. |
| Authentication token sharing | Separately reviewed secure token design | App Group storage alone does not configure Keychain access. Never put provider API keys in app or extension. |
| Microphone / Apple's dictation | No control of Apple's dictation UI; custom keyboards lack equivalent microphone access | Do not imply our keyboard preserves Apple's complete dictation/typing feature set. User can switch keyboards. |
| Host or keyboard switching | Lifecycle-driven cancellation and state invalidation | Extension can be dismissed/terminated. Never rely on background execution, memory survival or client cancellation reversing billed inference. |

A release keyboard needs usable keyboard input and a next-keyboard mechanism
(`needsInputModeSwitchKey`, `advanceToNextInputMode` / supported switching actions).
An AI-only overlay must not be assumed App Store compliant. Current keyboard
review rules, network-off functionality and data-use restrictions must be verified
before deciding release UI. Predictive typing, autocorrect, languages and native
feel are substantial work; a custom keyboard is not a free Apple keyboard toolbar.

## Proposed architecture and reuse

```text
Containing SwiftUI app
  onboarding / profile and relationship management / sessions / consent / deletion
       ↕ approved minimal shared settings + profile identifiers
Keyboard extension (UIKit controller, optional hosted SwiftUI assistance panel)
  ordinary input / switch keyboard / explicit context + goal / 3 suggestions
       ↓ shared request models, endpoint validation, safe errors and cancellation
Authenticated FastAPI generation service
  authorization / quotas / approved profile + relationship context assembly
       ↓ one common provider pipeline (no keyboard-specific model fork)
Hosted model → validation → extension → explicit user-selected insertion
```

Reuse current `ReplyClient`, wire models and cancellation ideas; extract a small
extension-safe shared Swift target only when approved. The current Package.swift
can compile Foundation code, but this does not prove an extension build or Apple
Observation compatibility. Keep keyboard UI/state lifetime separate from the
standalone composer. Shared generation services should not depend on SwiftUI app
navigation or pasteboard side effects.

`ios/project.yml` currently defines exactly one application target: no extension,
App Group/Keychain entitlements, provisioning or keyboard plist. A new extension
target and embedding configuration are necessary. `backend/app/main.py` currently
has no sessions, profile/history/context retrieval or feedback APIs. Its inputs
are only mode, incoming message, relationship, goal and optional draft. The style
utility and Apple verifier are disconnected foundations. Both modes currently require `incoming_message`, relationship and goal; a keyboard
with only a draft cannot automatically satisfy this contract. Approve draft-only
rewrite semantics or explicit context entry before changing the API; do not invent
an incoming message to satisfy validation. The owner's request
calls for a shared personalization engine that does not yet exist; do not claim
that linking the keyboard to today's endpoint produces personalized replies.

App-lifespan HTTP pooling benefits the backend, while the extension should reuse
an ephemeral client only for its active lifetime. Bound draft/context size,
network response size and in-flight work. Do not continuously scan or upload text
while the user types. Begin at most one generation when explicitly requested;
regenerate is another explicit request with another potential charge.

## Context, privacy and insertion strategy

1. Capture only the available editable text/selection after an explicit action.
   Clearly distinguish draft text from incoming conversation context.
2. When incoming context is missing, let the user type a short summary or use an
   explicit, permission-aware paste action if supported. Do not silently inspect
   the clipboard, screen-scrape, request accessibility privileges or read host data.
3. User selects a relationship/profile; do not automatically identify contacts or
   host application from unsupported/private APIs. Saved context remains governed
   by separately approved consent, retention and isolation rules.
4. Snapshot input, cursor/document identity where available, goal and relationship
   for a request. Changes invalidate suggestions; on return, recheck the active
   context and require confirmation if it differs. Available proxy context cannot
   prove the entire document unchanged, so do not promise atomic full-draft replace.
5. Insert ONLY the chosen response. Selection of a suggestion is not evidence that
   it was sent; capture feedback only with explicit approved semantics.
6. Store no raw keystroke/conversation history in extension defaults/logs. Proposed
   initial sharing is endpoint/non-sensitive preferences and identifiers, with
   secure session access designed separately. Do not persist drafts across hosts
   by default or silently resume a previous app's private suggestions.
7. Full Access must have a clear explanation of data sent, destination, purpose
   and denied/revoked behavior. Consent to keyboard installation/Full Access is not
   automatically consent to history retention, model training or feedback storage.

Recommended denied/offline behavior: ordinary typing and keyboard switching remain
available; remote assistance explains the prerequisite without queuing automatic
uploads for later. Main app setup may help users enable the extension, but the
keyboard should not depend on unsupported attempts to launch its containing app.

## Cross-application verification matrix

All entries below are **not tested**, not predictions or compatibility claims.

| Host | Status | Required test coverage |
| --- | --- | --- |
| Apple Messages / iMessage | Not tested | Compose, reply, selection, multiline, insertion, switching |
| Snapchat | Not tested | Chat composer, different field types, host blocking behavior |
| WhatsApp | Not tested | Individual/group compose, selection, insertion, lifecycle |
| Instagram DMs | Not tested | Compose variants, multiline, custom inputs, switching |
| Facebook Messenger | Not tested | Compose, selection, insert, navigation/dismissal |
| Hinge | Not tested | Chat versus prompts, field limits, custom inputs |
| Tinder | Not tested | Chat fields, host restrictions, insertion |
| Discord | Not tested | Multiline compose, mention context, selection |
| Telegram | Not tested | Compose modes, selection, insertion, switching |
| Other standard iOS hosts | Not tested | Text views/fields, search, numeric and secure controls |

Record device/iOS version, host version, field type, enabled/denied Full Access,
proxy context availability, selected-text behavior, insertion, cancellation,
rotation/accessibility and memory termination results. Include secure/phone-pad
negative controls. Do not commit real test conversations/screenshots.

When a host blocks the keyboard, it cannot be bypassed. Alternatives are voluntary
standalone assistance, an approved share extension only when the host supplies
content, or explicit user copy/paste. None guarantees the primary no-app-switch
workflow in blocked hosts. A share extension is another scope proposal, not an
already implemented fallback.

## Effort, latency and ongoing cost

Planning ranges, not measured delivery promises; assume experienced native iOS
engineering, working Mac/signing setup and timely decisions:

- Feasibility spike and text-proxy/Full Access/lifecycle harness: roughly 1–2
  engineer-weeks after approval and documentation access.
- Minimal single-language keyboard input, assistance panel and explicit insertion:
  roughly 3–6 additional engineer-weeks. More native typing parity can take much
  longer; third-party keyboard framework/library adoption needs separate review.
- Shared auth/personalization/context integration: not a small add-on; roughly
  4–8+ engineer-weeks depending on approved storage, import formats and retrieval.
  These foundations have not been completed in the current application.
- Cross-app, accessibility, interruption/privacy and device hardening: roughly
  2–4+ additional engineer-weeks, with overlaps possible and host-specific unknowns.

Keyboard integration itself adds no second inference engine or inherently new
paid model service. Explicit generations/regenerations incur the same input/output
cost as the shared engine; relationship history increases input unless bounded.
Insertion and ordinary typing do not require inference. No on-keystroke model calls.
Estimate cost from measured tokens × current official rates × generations, plus
approved hosting/storage and signing/distribution arrangements. Exact rates and
Apple program fees were not refreshed here. The existing $2 once-only integration
allowance does not cover keyboard evaluation, daily use, deployment or a new budget.
The existing campaign fingerprint mismatch remains a blocker, not fresh credit.

## Revised sequence and gates

Respect the owner's requested phase order, with a prerequisite privacy gate:

0. Reconcile missing original requirements as available; approve profile/history,
   identity, consent/deletion/isolation design before private message imports.
   Continue synthetic tests meanwhile. Verify current Apple contracts and local
   Xcode capability. This is a prerequisite to Phase 1, not a shortcut past it.
1. Personalization foundation: approved import, editable general profile and
   relationship-specific behavior; synthetic first. Exit: authorship attribution,
   isolation/deletion tests and measured profile behavior, not just stored history.
2. AI generation/rewrite: shared context assembly and three suggestions; generic
   baseline versus personalized human assessment. Exit: actual live responses,
   intent/authenticity evidence and a native build, within separately approved spend.
3. Keyboard prototype: own toolbar/assistance UI, Full Access states, shared API,
   safe user-selected insertion. Exit: actual signed/unsigned appropriate Xcode
   builds and device/proxy/lifecycle tests; no assumed Apple-keyboard injection.
4. Cross-app verification: fill the matrix with observed results and fallbacks.
5. Personal daily use: only after privacy/auth and budget approval. Feedback must
   distinguish inserted, edited and explicitly submitted/sent information.
6. Refinement/release: keyboard ergonomics, languages/accessibility, latency,
   quality, quota controls and privacy/review acceptance; release separately approved.

## Decisions requested before extension implementation

1. **Accept a separate Proofread keyboard** with our own toolbar, rather than a
   button injected into Apple's keyboard. This is the technically feasible path;
   keeping Apple's keyboard unchanged requires a different, host-dependent workflow.
2. Approve only a **small synthetic keyboard feasibility spike first**, after
   current Apple documentation/SDK validation. This proves proxy/insertion/Full
   Access/lifecycle behavior without storing private histories or choosing final UI.
   The product phases still prioritize personalization; the spike de-risks platform
   feasibility and is not a full keyboard rollout or permission to skip foundations.
3. Decide **draft-only rewrite versus mandatory context** for the keyboard.
   Recommend allowing an explicitly context-limited rewrite without pretending to
   see an incoming conversation; this requires a compatible API/product proposal.
4. Separately review final keyboard UI/typing scope, session sharing, App Group
   contents, privacy/retention and any test/deployment budget before integration.

Recommendation: accept the custom-keyboard constraint and authorize the narrow
synthetic spike as the first platform decision. Retain existing working components;
do not build full history retrieval, a full predictive keyboard or a separate AI
backend merely to demonstrate a toolbar.
