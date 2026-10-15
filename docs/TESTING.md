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

These tests compile the application's shared Foundation sources and verify networking contracts and composer state. Linux excludes the Apple Observation adapter; its state transitions are shared, but observation/SwiftUI wiring is not compiled here. The Swift package requires macOS 14+ for that adapter; iOS remains 17+. XcodeGen generation, actual Xcode build, signing and simulator/device acceptance must run on macOS and be recorded separately.

## Quality gates and security review

- Reproduce meaningful defects before fixing them; test both generate and rewrite where shared behavior changes. Preserve regression tests.
- Review relevant input/output validation, cancellation/error handling, private-data exposure, authentication/isolation and resource/cost bounds. Keep secrets/raw conversations out of fixtures, logs, commits and reports.
- Test actual expected behavior at the service boundary when appropriate; a PID, open port or zero-test run is insufficient.
- Record exact commands and passed/failed/skipped/unrun outcomes in `IMPLEMENTATION_STATUS.md`. Distinguish local tests, remote CI at a specific commit, native compilation and production acceptance.
- Use `git diff --check` and review the final diff before committing. Documentation-only changes require factual/link review rather than invented test coverage.

AI experiments and human-review workflows are documented in `AI_EVALUATION.md`; paid inference is never a default test gate.

## Authentication foundation and dependencies

Run `.venv/bin/python -m pytest -q tests/test_apple_identity.py` from `backend` for synthetic signed-token/key-rotation/resource-bound tests. No real Apple tokens or key fetches are used. See `AUTHENTICATION.md` for library boundaries; unit success does not establish Apple sign-in or session security.

After dependency changes, run `.venv/bin/python -m pip check` and audit the installed pinned package set. The October 15 audit used an isolated pip-audit tool with writable workspace caches and no project-tool dependency:

```sh
.venv/bin/python -m pip freeze > /tmp/proofread-python-freeze.txt
UV_TOOL_DIR=/workspace/.cache/uv/tools UV_TOOL_BIN_DIR=/workspace/.cache/uv/bin \
  uvx --cache-dir /workspace/.cache/uv --from pip-audit pip-audit \
  --cache-dir /workspace/.cache/pip-audit --disable-pip --no-deps \
  --progress-spinner off -r /tmp/proofread-python-freeze.txt
```

This requires advisory-service network access; report skipped/unavailable checks honestly. No known findings is not proof that a dependency or application is secure. Preserve TLS and artifact verification, and rerun affected regressions after dependency corrections.

Single evaluation output regression coverage lives in `tests/test_artifacts.py`:
serialization failure leaves no partial report, durability failure rolls back owned
output, UTF-8 JSON is private (0600), and existing reports cannot be overwritten.
These checks share the existing paired-writer regression suite.

Provider resource regressions (`tests/test_provider.py`) cover early stream stop
and closure, total deadline, exact size boundary versus one excess byte, and
rejection of compressed responses before decoding. Tests use MockTransport only.
