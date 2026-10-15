# Engineering decisions and unresolved approvals

The finalized PRD, SPEC, architecture research and approved UI designs are not present in this checkout. This record documents implementation choices and boundaries; it does not replace those source documents or approve provisional product decisions.

## Current implementation choices

- Preserve SwiftUI and the existing provisional FastAPI backend. Harden generate and rewrite together without redesigning the interface.
- Keep the deterministic mock as the default. Isolate test credentials and prohibit real HTTP transports in Python tests. No live model calls occur in CI or the offline evaluation CLI.
- Treat provider output as untrusted: validate structure, distinctness, nonblank content, length and completion status before returning suggestions. Surface safe 502/503 errors without upstream bodies.
- Compile the application's existing Foundation sources as a dependency-free Swift Package for Linux networking tests. This complements, and cannot replace, macOS/Xcode app and simulator validation.
- Start evaluation with invented cases, contract evidence and blinded human-review templates. Do not equate a valid response with good communication, intent fidelity or authentic style.
- Do not introduce persistence, private-history imports or a public personalization endpoint before authentication, consent, deletion and user isolation are designed and tested. The existing aggregate style extractor remains local and disconnected from generation.

## External prerequisites

- Reconcile the finalized source documents and approved workflows before consequential product, UX or architecture changes.
- The owner approved `gpt-5.4-mini` and a one-time $2 maximum for synthetic generate/rewrite integration testing. Official model/pricing/cap evidence was reviewed October 15; same-day artifact is outside Git and gives a two-call conservative reservation of $0.604608. Secure credentials/account availability remain missing. Refresh evidence on later dates and preserve the original ledger. See `AI_EVALUATION.md`; never place keys in chat, Git or fixtures.
- Run XcodeGen, an actual Xcode build, simulator/device acceptance and signing on macOS. Linux Foundation tests establish only shared client behavior.
- Git read access works. GitHub API access initially returned HTTP 403 but now succeeds; the backend workflow for the original `main` commit `15169a6` completed successfully. New branch checks are separate. Official OpenAI documentation access also recovered; documentation compatibility is verified, but authenticated model availability/live inference is not.

## Permanent engineering workflow

At the owner's direction, root `AGENTS.md` now establishes autonomous routine implementation, consequential clarification throughout development, explicit approval boundaries, intelligent tool/subagent use, TDD, security review, feature branches, validated commits/PRs and durable project memory. Detailed procedures live in `ENGINEERING_PROTOCOL.md`; actionable handoff work lives in `NEXT_TASKS.md`. This does not approve new spending, product changes or releases.

The full owner-supplied protocol additionally makes protected-branch merges explicitly approval-bound and adds durable `TESTING.md`/`AI_EVALUATION.md` procedures. Existing cloud isolation remains sufficient; no worktree is needed for routine delegation.

Composer state uses the standard iOS 17 Observation adapter around shared Foundation logic, preserving the existing form/navigation. Linux tests omit that adapter because the Debian toolchain's Observation library fails linking; no runtime/security bypass was used. The Swift package requires macOS 14 for Observation. Actual Apple compilation remains a gate, not an inferred success.

`AUTHENTICATION_PROPOSAL.md` is a concrete proposal for the next identity foundation. Approval is pending; token-verification implementation, sessions and private-data handling are not authorized by the proposal itself.

These implementation choices do not authorize deployments, recurring expenses, production releases, private-data retention policies or finalized designs.
