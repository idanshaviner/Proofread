# Alternatives to keyboard-only context — research, not implementation approval

Research date: October 30, 2026 (owner timezone). Scope: personal iMessage and
Snapchat on iPhone. No screen capture, OCR pipeline, shared data container, API
integration, private history access or paid service was implemented or exercised.

## Conclusion and correction

“No direct keyboard/chat API” does not mean “no possible visual context workflow.”
A user-authorized screen-sharing/capture session plus local OCR is a plausible
way to obtain visible conversation text while a keyboard provides the interface.
It does not grant access to hidden messages or silently read another app's data.
The previous categorical framing was too broad. This remains a feasibility
hypothesis until the actual supported capture API, background lifetime and target
hosts are tested on the owner's device.

Changing only keyboard code cannot confer screen-reading permission. The likely
change is the context-acquisition subsystem, with the existing keyboard, common
backend and eventual personalization engine retained.

## Evidence obtained and its limits

Apple developer pages and Snap developer pages returned proxy403 during the prior
read attempts; no fresh App Review or Snapchat policy verification is claimed.
The following public maintained sources were successfully fetched HTTP200:

- Microsoft .NET iOS bindings: [ReplayKit](https://github.com/dotnet/macios/blob/main/src/replaykit.cs).
  `RPSystemBroadcastPickerView`, `preferredExtension`, `showsMicrophoneButton`,
  `RPBroadcastSampleHandler.processSampleBuffer`, lifecycle callbacks and
  application-info annotations are exposed. These substantiate a legacy public
  user-started capture route, not its fitness for this product.
- Microsoft bindings: [ScreenCaptureKit](https://github.com/dotnet/macios/blob/main/src/screencapturekit.cs).
  Current main marks `SCContentSharingPicker`, `SCStream`, stream outputs and
  configuration as iOS27+, and marks key paths unsupported on iOS simulator.
  ReplayKit main bindings mark broadcast sample handlers deprecated at iOS27
  (“No longer supported”) and point the picker to SCContentSharingPicker.
  This is a critical version gate, not a reason to blindly implement ReplayKit.
- Microsoft bindings: [Vision](https://github.com/dotnet/macios/blob/main/src/vision.cs)
  exposes `VNRecognizeTextRequest` and language/recognition settings for local OCR.
- Microsoft bindings: [Messages](https://github.com/dotnet/macios/blob/main/src/messages.cs)
  exposes MSConversation participant IDs, selected MSMessage and composition
  methods; this is not a transcript-reading interface.
- Snap-maintained [Camera Kit README](https://github.com/Snapchat/camera-kit-ios-sdk)
  describes AR camera integration, not a personal-chat reader. Reading this one
  SDK does not constitute exhaustive proof of all Snap platform capabilities.

These are maintained vendor binding sources / a Snap SDK, not Apple's current
SDK headers or a tested native contract. Main may contain prerelease/version-
specific work. The owner's supplied log names Xcode27.2/iPhoneSimulator27.2;
the owner subsequently reports the phone runs **iOS27.0.1**. These are compatible
version signals, not proof of capture behavior. Verify
local iPhoneOS SDK headers and device OS before selecting an implementation.
`ios/scripts/inspect-capture-sdk.sh` collects public header availability evidence
without recording anything or changing the project. No symbol lookup grants
capture permission or proves cross-app/background capture works.

Official references to validate on an accessible network:
[ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit),
[ReplayKit](https://developer.apple.com/documentation/replaykit),
[Vision](https://developer.apple.com/documentation/vision), and
[App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).

## Candidate approaches

| Approach | Potential benefit | Hard limits / assessment |
| --- | --- | --- |
| Modern system content-sharing picker + local OCR | Permissioned visual context; may reduce repeated screenshot actions | Verify iOS availability, selection scope, continued capture while host foregrounds, entitlement/background requirements and device support. Current bindings flag iOS27+; not assumed working. Priority feasibility investigation on a matching device. |
| Legacy ReplayKit Broadcast Upload Extension + local OCR | User starts a broadcast; extension receives video samples across an authorized screen-sharing session | Version-dependent/deprecated in retrieved main bindings. Do not confuse app-only RPScreenRecorder capture with system broadcast. New extension and reviewed cross-process context sharing needed. Legacy alternative only after SDK/OS verification. |
| Screenshot → share → local OCR | Simpler, discrete, user-selected context acquisition | More taps, may switch UI; cannot promise clipboard availability or keyboard return. Snapchat may detect/notify screenshots. Good fallback, not automatically approved. |
| Messages extension | App-specific composer UI inside iMessage | Does not grant general access to prior SMS/iMessage bubbles; does nothing for Snapchat. It is a UI alternative, not the context solution. |
| macOS Messages relay | Potentially uses user's Mac and synchronized Messages data | New always-available companion, explicit local-data permissions, secure phone relay, schema/privacy/retention work; not a public iOS transcript API. No Snapchat solution. Not preferred for first consumer prototype. |
| Shortcuts / on-screen content / App Intents | User-triggered automation where the host explicitly supports the content | Not universal access to Snapchat or iMessage transcripts; must prove per-host sharing support. No route to silently query any foreground app. |
| Notification service / third-party keyboard tricks | Superficially attractive small implementation | Notification extensions cannot inspect other apps' notifications; App Groups don't cross unrelated developers; Full Access isn't screen access. No supported universal solution here. |
| Android accessibility or screen capture | Different OS may offer other user-authorized context inputs | Major platform/product change and policy/privacy constraints; even Android keyboards alone don't receive chat transcripts. Not an iOS fix; no Android change approved. |
| Private APIs, sandbox exploits, jailbreak, session interception | Could evade platform boundaries on modified devices | Fragile, broad private-data risk, device/account/release incompatibility. No instructions or implementation recommended. Do not use these to promise a reliable consumer product. |

## Proposed capture-assisted architecture to test

1. In Proofread, the user explicitly starts a system-authorized capture session.
   Choose the modern or legacy adapter only after SDK/device checks. Do not hide
   prompts, indicators or host capture detection. No microphone/audio needed.
2. Return to the desired conversation and select the Proofread keyboard. The
   keyboard remains the assistance UI; it cannot overlay arbitrary host UI or add
   buttons to Apple's keyboard.
3. Tap **Use visible conversation**. Process a bounded fresh frame only for this
   explicit request. Avoid continuous OCR or automatic model calls. The capture
   subsystem may still receive screen frames throughout the session: discarding
   frames is not the same as never receiving them, and users must understand this.
4. OCR locally and show a short editable context preview inside the keyboard.
   Separate message text, uncertain speaker assignment and inferred order. Do not
   silently assert who sent which message; do not require a model to guess.
5. User chooses audience and intention, confirms the text, then explicitly generates
   three suggestions using the SAME generation/personalization service. This
   requires separately reviewed context API, auth/quota and provider setup.
6. Validate the active field/context before insertion; never auto-send.
7. Stop capture explicitly and on timeouts/errors/revocation. Expire pending requests
   and extracted context; never reuse stale text from a different conversation.

The keyboard can obscure the bottom of the conversation. Context is limited to
what capture actually exposes; it does not include offscreen history, disappearing
content already gone, protected surfaces, or an app database. It may be incomplete
or blacked out. App annotations, where provided by a verified API, can inform a
host allowlist, but must not be assumed complete, immediate or tied to every frame.
Do not invent host identity or rely only on OCR to exclude sensitive applications.
The retrieved iOS27 bindings exclude macOS-style application selection and several
picker filtering properties from iOS. Do not promise an iPhone app allowlist just
because a similarly named macOS API exists.

## Privacy, compatibility and operational gates

- Screen capture is a substantial new privacy scope. Require explicit session
  consent, clear capture status, an obvious stop control, and synthetic test data
  first. Previously approved keyboard fixtures did not authorize capture.
- Initially disable audio and upload neither images nor extracted text. No LLM
  or private conversations are needed to test whether a bounded frame can be
  processed locally. Do not claim a screen broadcast means a video must be saved
  or sent over the Internet; process in memory if the API allows that architecture.
- Cross-process delivery needs review. An App Group file containing extracted text
  is still persistence even if short-lived; choose protection, consume-once IDs,
  expiry, deletion and synchronization explicitly. Do not call it “memory only.”
  Never place raw frames or tokens in shared defaults as a shortcut.
- Snapchat may detect capture, notify participants, restrict output or change
  behavior by version/content. Test only with owned test accounts and synthetic
  conversations. Do not attempt detection suppression or guarantee stealth.
- Screen capture, local OCR and capture-session background processing have device
  thermal/memory/battery costs. Bound frame dimensions, retain at most a bounded
  number of frames, process on demand, and measure. No invented frame-rate,
  memory quota, p95 latency or battery guarantee is provided here.
- System capture permission and keyboard Full Access are separate permissions;
  neither constitutes cloud processing, history retention or model-training consent.
- App Review acceptance for a recording/OCR keyboard is not established. Current
  rules and platform-supported intended usage need verification before release.

## Proposed experiment and go/no-go criteria — approval needed

A narrow **device-only, synthetic capture/OCR experiment**, not a product rollout:

1. Inspect actual SDK headers and confirm device iOS. Select a documented capture
   adapter; prove capture persists in the needed foreground/background arrangement.
2. Start/stop capture with system UI; use a controlled synthetic test screen first.
3. Extract one bounded frame's text locally with no audio, storage, network or AI.
   Confirm orientation, missing/protected frames, interruption and permission revocation.
4. With owned test accounts, record iMessage/Snapchat behavior, including observable
   capture notifications/restrictions. Discard the approach for unsupported hosts
   rather than bypassing them.
5. Only then propose a separate minimal keyboard/context bridge with a reviewed
   transient data policy and evaluate readable context confirmation UX.

Exit: actual device evidence of capture access, interruption cleanup, OCR accuracy,
latency and host behavior. Fail if capture is unavailable, backgrounding kills the
pipeline, host restrictions make it unsuitable, or privacy/review burden exceeds
value. No transcript guarantee or working product claim follows from API existence.

Recommendation: **retain the keyboard; investigate permissioned visual context**.
First choose modern ScreenCaptureKit versus legacy broadcast from the actual SDK
and phone OS. Prefer screenshot/share if session capture is too intrusive or host
behavior makes it unsuitable. No implementation proceeds under research-only
permission; ask approval for this explicit capture privacy scope and experiment.
