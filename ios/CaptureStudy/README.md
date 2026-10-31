# Local capture study — separate developer app

This app is a study, not the keyboard or a production release. It needs iOS27+ on
a physical device and the matching Xcode SDK. It has no backend, provider key,
keyboard, App Group, audio output, recording-file output or cloud upload.

From this folder:

```sh
xcodegen generate
open ProofreadCaptureStudy.xcodeproj
```

Select the ProofreadCaptureStudy target → Signing & Capabilities → Automatically
manage signing → your Personal Team, then choose your iPhone as destination and
press Command-R. If the bundle ID is unavailable, choose your own unique ID.
Do not modify the existing Proofread keyboard/app signing settings for this study.

First run the synthetic OCR self-test. Then, while displaying only the invented
study text, press Start system sharing prompt and accept the system UI if you
want to test it. Press Read one frame locally once capture is active. Stop and
clear afterward. The first capture mode shares this app only; leaving/backgrounding
the app stops it. System permission transitions alone should not stop the capture.

Check denied/cancelled permission, stop during OCR and 30-second expiry. Capture
indicators and host detection are never hidden. There is no Snapchat/iMessage
access in this first-stage app. Cross-app/background behavior requires another
controlled study step after this adapter builds and works on the phone.

Native compilation and capture/OCR behavior are not verified in the Linux
workspace. Send the first Xcode error or on-device study result. No real chat
screenshots, private text or credentials are needed in the report.

If the system reports a stop failure, the study deliberately blocks restarting.
Stop sharing with iOS system controls and close/relaunch the study before trying
again. Do not assume a local Stop tap guarantees immediate OS capture shutdown.
If the capture frame is rotated, empty, protected or rejected, record that result;
orientation accuracy and host behavior have not been verified.
