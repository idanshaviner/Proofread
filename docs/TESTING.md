# Testing and verification

Use invented messages only. Mock inference is the development and CI default; Python tests clear developer provider credentials and block real HTTP transports. Never disable TLS/signature verification, hide failures or claim that valid output establishes AI quality.

## Backend

From `backend` with Python 3.11+ (current cloud: Python 3.12):

```sh
.venv/bin/python -m pytest -q
```

For a focused change, run its regression test first and confirm the intended failure, then implement and rerun affected checks. Run the full backend suite for shared API/provider/evaluation changes. Dependency refresh follows `requirements.txt`; no dependency changes are required for routine tests.

## Shared Swift sources and local API

From the repository root in the prepared Linux cloud environment:

```sh
SWIFT_BIN=/workspace/toolchains/swift-6.1.3-RELEASE-debian12/usr/bin/swift bash ios/scripts/test-networking.sh
```

The signed-toolchain installer and portable macOS instructions are in `ios/README.md`. Default tests explicitly skip the optional live-local API check. To exercise actual URLSession traffic, start `PROOFREAD_PROVIDER=mock .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` from `backend`, verify `/health`, then run:

```sh
SWIFT_BIN=/workspace/toolchains/swift-6.1.3-RELEASE-debian12/usr/bin/swift PROOFREAD_TEST_API_BASE_URL=http://127.0.0.1:8000 bash ios/scripts/test-networking.sh
```

These tests compile the application's shared Foundation sources and verify networking contracts. They do not compile SwiftUI/UIKit or run an iOS simulator. XcodeGen generation, actual Xcode build, signing and simulator/device acceptance must run on macOS and be recorded separately.

## Quality gates and security review

- Reproduce meaningful defects before fixing them; test both generate and rewrite where shared behavior changes. Preserve regression tests.
- Review relevant input/output validation, cancellation/error handling, private-data exposure, authentication/isolation and resource/cost bounds. Keep secrets/raw conversations out of fixtures, logs, commits and reports.
- Test actual expected behavior at the service boundary when appropriate; a PID, open port or zero-test run is insufficient.
- Record exact commands and passed/failed/skipped/unrun outcomes in `IMPLEMENTATION_STATUS.md`. Distinguish local tests, remote CI at a specific commit, native compilation and production acceptance.
- Use `git diff --check` and review the final diff before committing. Documentation-only changes require factual/link review rather than invented test coverage.

AI experiments and human-review workflows are documented in `AI_EVALUATION.md`; paid inference is never a default test gate.
