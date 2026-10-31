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

## Owner SDK evidence and first native adapter

The owner supplied the inspector output: Xcode27.2 build27B52, iPhoneOS SDK27.2.
ScreenCaptureKit headers explicitly expose picker/filter/stream APIs on iOS27.
They confirm mic/camera picker controls and `capturesAudio`, width and height;
minimumFrameInterval, queueDepth, sourceRect and several desktop-style options
are unavailable on iOS. Two legacy ReplayKit headers were absent at checked paths.
The owner reports iOS27.0.1. Do not request this same evidence again.

The first adapter uses the modern system picker with current-application-only
selection. It does not promise cross-app or background delivery. A standalone
`ios/CaptureStudy` XcodeGen target launches the study without a launch variable,
backend or existing app/keyboard changes. New capture source still requires an
actual device build/run; Linux syntax checking cannot validate SDK import names,
entitlements, permission behavior or sample delivery. See that folder's README.

No recording output is registered. Audio is disabled; the adapter must reject a
filter enabling microphone/camera rather than processing it. A lock-gated receiver
admits only a requested frame, and late work is invalidated on stop/session expiry.
OCR uses local Vision only. First prove this current-app harness on invented text,
then evaluate a separately explicit screen-wide mode within the approved study.
Context transfer into the keyboard is not implemented in this stage.

## First device evidence and optional Notes switch test

Owner screenshot shows the local OCR result reproducing the current study app's
interface, including its sharing-active status and labels. This supports one actual
current-app screen-frame/OCR success on the owner's phone. It does not prove
cross-app capture, source freshness, notification behavior or keyboard transfer.

An optional wider-screen synthetic test is now source-implemented. The own-app
mode remains the default. User must turn on the Notes test and confirm that only
invented text is displayed, then accept the system picker. After sharing starts,
press Capture in 5 seconds and switch to a NEW Notes note with a unique invented
phrase NOT shown in the study app. Change the phrase every run. Return within20s,
inspect output and Stop. Disable private notification previews/use an appropriate
Focus during the test; never open real chats to test this pipeline.

The stream receiver drops callbacks before the five-second threshold and after
the original30s deadline, before actor handoff. A locked Foundation gate admits
one token; tests cover threshold, expiry, invalidation, clock failures and parallel
consumers. This gates callback receipt time, NOT sample presentation-time freshness.
If iOS suspends the process, callbacks/timers may stop or resume late. Result access
expires on resume, but an OS capture indicator is not guaranteed to stop at exactly
30s while backgrounded. Return promptly and stop using system controls if necessary.
Own-app mode still stops on background; the optional switch test is deliberately
different. A result containing only study labels, blank text or an old phrase is
not a passing cross-app result. No keyboard bridge, App Group, network or AI added.
