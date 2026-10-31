# Device feedback and feasible keyboard workflow

Owner reports successful physical iPhone installation/launch, then connection
failure in the standalone composer. This is device-launch evidence, not verified
keyboard insertion, cross-app behavior, live AI or passing tests. The preceding
Mac log also showed a successful native build followed by two networking fixture
failures (four assertions): URLSession did not expose JSON in `httpBody` on that
platform. That test-harness issue remains to fix; do not report a fully green Mac
suite.

## Connection diagnosis

Current project config sets `PROOFREAD_API_BASE_URL` to
`http://127.0.0.1:8000`. On physical iPhone that is the phone, not the Mac/cloud
backend. No reachable server was bundled or deployed by the approved offline
keyboard spike. An Xcode scheme environment variable can override this setting;
confirm the effective configuration if the owner changed it. Device Internet
connectivity alone cannot fix a loopback endpoint.

The app and keyboard are separate surfaces: tapping the app icon opens the
containing SwiftUI app; the extension must be enabled in iOS keyboard settings
and selected through the globe control. This keyboard is deliberately offline
with fixed suggestions, so it makes no request even when Full Access is enabled.
A reachable trusted HTTPS endpoint, secure session/abuse perimeter and configured
provider are separate gates before real/private conversation use. Never put a
provider API key into the iPhone build or expose an unauthenticated billed API.

## Supported experience recommendation — pending scope/context agreement

A third-party keyboard cannot place controls in Apple's keyboard or inspect chat
bubbles elsewhere in another app. Full Access does not grant either capability.
Keep the containing app for setup/profiles; daily assistance lives in our own
selected keyboard. The app cannot make this replacement indistinguishable from
Apple's typing/dictation implementation.

Proposed compact flow:

1. Tap Proofread in our keyboard toolbar; an assistance panel expands inside the
   keyboard area, keeping the host conversation visible above it.
2. Context card says exactly what is available: current draft or incoming text
   explicitly pasted/entered by the user. Never imply screen-reading or silently
   read the clipboard. Do not submit anything until the explicit generation action.
3. Audience and intention appear together as concise controls. For example,
   audience “Friend” / “Colleague” / user-entered description; intention “Accept” /
   “Decline politely” / custom text. These are proposed examples, not approved final
   labels or persistent recipient profiles. Avoid unsupported contact detection.
4. Generate three responses with distinct useful approaches, shown as readable
   cards in the panel. The generation context/personalization contract must be
   implemented and evaluated; today's fixed examples cannot satisfy this.
5. Tap a card to insert at a validated cursor. Block stale context and active
   selection in the initial insertion-only scope. No automatic sending. Editing
   happens in the host field; regenerate is explicit and potentially billable.

Separate states: permission missing, backend unavailable, context missing,
generating, stale context and suggestions. Preserve user-entered goal/audience
in memory for the active interaction without automatically retaining host text
across applications. Keyboard layout, accessibility and interruption need native
testing. Real AI networking, new context fields, personalization and privacy
permissions exceed the currently approved offline spike.

## Next decisions and work

- Confirm whether explicit user-supplied incoming context is acceptable. Automatic
  cross-app conversation reading is not an implementable keyboard-API option.
- Confirm/establish a reachable HTTPS development backend with a safe access
  boundary. Then validate connectivity using synthetic data first. No production
  deployment or external tunnel service is silently introduced.
- Secure provider key and approved campaign state/current evidence are still
  prerequisites to paid inference; the existing $2 campaign is not renewed.
- Fix Mac URLProtocol request-body assertions to handle `httpBodyStream`; rerun
  tests on Mac. That is a routine regression fix independent of UX decisions.
- Add a targeted physical-device configuration diagnostic instead of implying a
  generic Internet fault when the known endpoint is loopback.
