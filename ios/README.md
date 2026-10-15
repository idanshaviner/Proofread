# Native iOS development harness

SwiftUI app target defined by XcodeGen. **The application has not been built or simulator-tested in the current Linux environment.** Its Foundation models, endpoint configuration, and URLSession client also compile independently as a Swift Package, allowing meaningful networking tests on Linux without claiming iOS verification.

On a Mac with Xcode and [XcodeGen](https://github.com/yonaskolb/XcodeGen) installed:

```sh
cd ios
xcodegen generate
open Proofread.xcodeproj
```

Start the backend locally from the repository root using `cd backend && PROOFREAD_PROVIDER=mock uvicorn app.main:app --reload`. iOS Simulator can reach `http://127.0.0.1:8000`; a physical iPhone requires a reachable HTTPS endpoint. Signing in Xcode remains required. The interface remains a developer harness, pending reconciliation with the approved design.

Configure the endpoint using the `PROOFREAD_API_BASE_URL` Xcode build setting or the same variable in the scheme's Run → Arguments → Environment Variables. Launch variables take precedence. HTTPS endpoints may include a path prefix. HTTP is permitted only for localhost/loopback simulator development. Invalid configuration displays a local configuration error; credentials, queries and fragments in endpoints are rejected.

Run the shared networking tests with Swift 5.9+ (verified here using the signed official Swift 6.1.3 Debian 12 toolchain on Debian 13):

```sh
cd ios
bash scripts/test-networking.sh
```

For a fresh Debian 12/13 x86_64 cloud machine, `bash ios/scripts/install-swift-linux.sh` from the repository root installs the pinned official toolchain under `/workspace/toolchains`. It requires `curl`, GnuPG, a system C/linker toolchain and the usual Swift runtime libraries (already present in this cloud machine), verifies the archive's detached signature against the expected Swift 6 release fingerprint, and reuses verified installation outputs. Downloaded artifacts stay under `/workspace/.cache/proofread-swift-toolchain`. TLS and signature verification remain enabled.

The script stores caches in ignored `.build/` for cloud machines with a read-only home directory. Set `SWIFT_BIN` to an absolute Swift executable when it is not on `PATH`, for example `/workspace/toolchains/swift-6.1.3-RELEASE-debian12/usr/bin/swift` in the prepared cloud environment. The package has no external dependencies. Tests cover generate/rewrite JSON, actual synthetic backend response fixtures, timeouts/cancellation, safe validation/provider errors, malformed responses, candidate validation and endpoint configuration. Backend tests cross-check those fixtures against real FastAPI output.

To exercise actual URLSession traffic against the local mock backend, start it on port 8011 in another terminal, then run:

```sh
PROOFREAD_TEST_API_BASE_URL=http://127.0.0.1:8011 bash scripts/test-networking.sh
```

This opt-in integration check exercises generate, rewrite and HTTP 422 handling; otherwise it is explicitly skipped. Use only synthetic messages and the deterministic mock provider. It does not establish live AI generation quality.

The shared `ComposerModel` owns input validation and request state. Required fields enforce the API's Unicode scalar limits (incoming message/draft 10,000, relationship 200, goal 500); generate omits and ignores the dormant draft. Editing any input or switching generate/rewrite invalidates the active request, cancels it, and clears suggestions, errors and the copied marker. Request identity prevents late success/error from replacing a newer result or changing its loading state even if a generator ignores cancellation. Copy actions resolve current candidate text; view disappearance cancels pending work. Continuation-driven tests exercise these transitions without real-time sleeps.

On macOS 14+, `swift test` runs the same shared suite. The iOS 17 SwiftUI app uses standard Observation to observe the model; Linux compiles the identical Foundation state transitions without Apple's observation adapter. Apple observation and SwiftUI wiring have not been compiled here. XcodeGen generation and an actual Xcode app build plus simulator/device acceptance remain separate required checks; Linux cannot perform them.
