# Approved local-only capture/OCR feasibility study

Owner approved the proposed synthetic experiment and accepts possible Snapchat
capture notifications. This is not permission to suppress detection, record real
chats, upload screen contents or deploy a service. Use a controlled synthetic
screen first; Snapchat testing requires owned test accounts/consenting people.

## Implemented preparation, not working capture

`CaptureStudySession` is a Foundation gate for one pending result, bounded text,
30-second session expiry, invalidation and late-result rejection. It holds no image
and uses no network/disk. `CaptureStudyView` is an optional main-app self-test that
creates a fixed invented text image and calls on-device Vision OCR. It has Stop,
expiry and disappearance cleanup. It does NOT capture the screen or connect to
the keyboard. Native Vision execution is unverified here; source syntax is not an
iOS build. No screenshots, microphone/audio, photo library, App Group or new
entitlements were added.

The opt-in main-app launch variable is `PROOFREAD_CAPTURE_STUDY=1`. New files need
source membership via XcodeGen; preserve/reapply your device signing settings if
regenerating. Do not expect existing downloaded source bundles to contain this
new study screen. A new signed binary is required before it can run on a phone.
Backend keys/services are unnecessary for this local self-test.

## Required SDK evidence before capture implementation

Run the read-only `ios/scripts/inspect-capture-sdk.sh` on the Mac with Xcode.
It reports version and selected public header declarations, not user data. Send
the output. The owner reports iOS27.0.1 and previously ran Xcode27.2, but secondary
API bindings are insufficient to choose capture architecture or promise cross-app
background behavior. Direct Apple documentation remains blocked here.

After that evidence, implement only a minimal permissioned capture harness and
verify with a synthetic test screen: user-start/stop, denied/revoked permission,
frame delivery while another app foregrounds, image orientation/protected frames,
OCR availability, one-request processing and resource bounds. No cloud upload or
model calls. Keyboard cross-process context sharing remains a separate design
step: an App Group text file would be persistence and must not be mislabeled as
memory-only. Nothing in this preparation automatically starts capture.

## Native self-test acceptance (unrun)

On a Mac/device build with the study launch variable set, press Run synthetic OCR.
Verify recognized text matches the invented fixture, Stop immediately clears text,
30-second expiry clears results and late completion cannot restore them, navigating
away discards results, and no network activity or saved image appears. This proves
only local OCR of an app-generated image, not permission to read iMessage/Snapchat.
All real capture/session/host compatibility claims remain pending actual testing.
