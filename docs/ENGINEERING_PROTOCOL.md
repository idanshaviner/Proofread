# Autonomous Engineering Operating Protocol

This procedure supports root `AGENTS.md`, the automatically discoverable entry point for Codex tasks in this repository. Current user instructions and applicable execution/security policies take precedence. The protocol authorizes routine engineering within the owner's scope; it does not settle provisional product decisions.

## Work loop

1. Read the root instructions, project memory and affected code; inspect Git status, recent history and available capabilities. Discover useful MCP/server capabilities before use; confirm an integration is connected rather than assuming access. Use existing tools when a missing integration is unnecessary. Preserve existing user work. Prefer the existing isolated checkout, without creating a worktree unless requested.
2. Select the highest-priority unblocked task from the current user request and `NEXT_TASKS.md`. Define a small observable outcome and required checks. Do not turn missing source documents or optional preferences into blanket implementation blockers.
3. For behavior changes, first write or run a regression test that fails for the intended reason. Implement a small vertical slice, then refactor with tests passing. Exercise both generate and rewrite when their shared contract changes. Keep external inference mocked in CI.
4. Use official documentation for uncertain technical facts. Use relevant available MCP integrations and tools rather than inventing access or results. Delegate independent tasks to parallel agents when beneficial; assign nonoverlapping files where possible, communicate interfaces, and review their code and actual test evidence before integration.
5. Review the diff for correctness, security, privacy and regressions. Check untrusted input/model output, accidental credentials or raw-message logs, authorization/isolation, transport verification and resource/cost bounds where relevant. Do not disable verification or weaken assertions to get a pass.
6. Run meaningful targeted tests, then the relevant integration/regression checks. Diagnose failures and rerun affected checks after corrections. Keep passed, failed, skipped and unrun outcomes distinct. Use actual Xcode/macOS for native app claims; Linux Foundation tests verify only shared sources.
7. Update durable memory and make a validated, focused commit. Continue the next unblocked task without an approval checkpoint for routine work. Reassess scope as new evidence or user steering arrives.

## Clarification and approval throughout development

Clarifying questions are not limited to planning. Ask as soon as uncertainty could materially change user intent, acceptance criteria, public contracts, privacy, architecture, cost or release behavior. Explain why it matters, offer reasonable options, recommend one with technical/product reasoning, state each consequence and identify independent work. Batch related decisions when useful. Pause that dependent action; continue safe independent work. Routine reversible implementation details remain autonomous.

Before an approval-bound action, prepare the concrete proposal, code/diff or validation evidence as far as existing authorization permits. Approval is required for significant UX/navigation or feature changes, material architecture deviations, core infrastructure/framework/database/AI-provider switches, important privacy/consent/retention decisions, new recurring costs or increased spending, destructive actions, protected-branch merges, deployment and App Store/production release. Also ask when multiple consequential options would produce meaningfully different product outcomes. Reuse recorded approvals exactly within their scope; do not renew a one-time allowance or treat elapsed time, a tool's availability, or silence as permission. Never request secret values in chat; inspect binding names/presence and use secure settings. New integrations needing elevated access, paid resources or meaningful data exposure require approval; do not install unnecessary services.

## Branches, commits and pull requests

- Create a descriptive feature branch before changes, or continue an existing branch for the same task. Do not reset, overwrite or delete user changes. Do not force-push or rewrite shared history as routine cleanup.
- Keep commits reviewable and focused. Run checks appropriate to the final diff before committing; record actual failures and platform limitations. Inspect documentation-only changes for accuracy and discoverability.
- Open or update a pull request for review when the remote workflow is authorized and accessible. Describe the problem, resulting behavior, validation and material limitations. Preserve the project's PR template. A draft PR is appropriate while external checks remain pending.
- If remote push, API access or credentials are blocked, retain the local branch/commits and record the exact blocker plus a ready PR description in the handoff. Do not fabricate a PR URL, repeatedly retry unchanged failures, request unnecessary tokens, or discard local work. Continue independent implementation.
- Merge/release only under repository policy and the owner's authorization; significant product/security decisions and production releases retain their approval boundaries.

## Durable memory and lifecycle

- `IMPLEMENTATION_STATUS.md`: current implemented capabilities, actual commands/results, environment/platform limitations and blockers. Distinguish current-instance validation, remote CI, deployment and new-task restoration.
- `DECISIONS.md`: durable technical choices, rationale, provisional assumptions, explicit owner approvals and limits. Do not convert reconstructed documents into finalized requirements.
- `NEXT_TASKS.md`: ordered next actions with observable acceptance criteria, dependencies, and completed/blocked state. Link material unanswered requirements in `OPEN_REQUIREMENTS.md` rather than repeating questions.
- `TESTING.md`: reproducible commands, meaningful quality gates and platform distinctions. `AI_EVALUATION.md`: baselines, experimental records, metrics and limits on conclusions. Keep `README.md` consistent with actual behavior.
- Update these records when the implementation or evidence changes, and before a handoff/context transition. Store no credentials or private conversation content in project memory.

Continue while the execution lifecycle supports useful work; do not end just because a milestone passed. End with verified results and a resumable handoff when the requested slice and useful independent follow-through are complete, a concrete external blocker prevents further useful progress, or execution limits require yielding. Do not imply processes, agents or future work will continue without an active supported execution context.

## Evidence and startup priorities

Optimize for useful consumer functionality, privacy/trust, reliable implementation, fast measured learning, maintainability and controlled cost. Proactively fix straightforward missing tests, errors, fragile contracts, accessibility defects and security issues within approved scope. Research must lead to experiments or code; do not add vector infrastructure, elaborate pipelines or fine-tuning without evidence.

Use strong generic baselines and progressively personalized experiments; measure authenticity, intent preservation, contextual relevance, naturalness, usefulness, diversity, preference and editing effort. Record limitations and noisy outcomes rather than claiming superiority. Source written, compiled code, passing tests, integrated behavior, live-model evaluation and production readiness are separate claims.

Prefer two or three genuinely independent workstreams with established interfaces, file ownership and acceptance criteria; reduce parallelism when integration or resource costs dominate. Review agents' results and run shared regression checks after integration. Existing cloud isolation is sufficient unless a worktree is explicitly requested.

Provide milestone updates with Completed, Testing, Next, Decisions Needed and Risks information where relevant. Include real commit/PR/test evidence, surface only founder decisions that matter, and avoid repetitive reports. GitHub is the persistent engineering source of truth: push validated branches and maintain PRs when authorized access exists, without force-pushes or protected-branch merges.
