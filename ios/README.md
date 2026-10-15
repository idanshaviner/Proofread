# Native iOS development harness

SwiftUI app target defined by XcodeGen; **not built or simulator-tested** in the current Linux environment.

On a Mac with Xcode and [XcodeGen](https://github.com/yonaskolb/XcodeGen) installed:

```sh
cd ios
xcodegen generate
open Proofread.xcodeproj
```

Start the backend locally using `cd backend && uvicorn app.main:app --reload`. iOS Simulator can reach 127.0.0.1:8000, but a physical iPhone cannot. For a device use a reachable HTTPS endpoint instead. UI is a developer test harness, not a finalized approved design. Signing in Xcode remains required.
