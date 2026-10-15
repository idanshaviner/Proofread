# Proofread PRD — provisional reconstruction
**Not an imported finalized PRD.** Reconcile with the final ChatGPT Project PRD before treating as authoritative.

## Problem and goal
People need help sending better texts without sounding generic or unlike themselves. Proofread should help them communicate naturally, appropriately and confidently.

## Audience
Initially college students and young adults, especially social and dating chats; professional communication later.

## Core MVP use cases
**Generate:** user pastes an incoming message, specifies recipient/relationship, context and communication goal, receives three concise distinct suggestions, edits or copies one.
**Rewrite:** user supplies an existing draft with relevant context, receives three voice-preserving rewrites and can edit/copy one.
**Progressive learning:** with explicit consent, import as much suitable message history as feasible, start with general style and gradually learn recipient-specific patterns, allow explicit preference/feedback corrections.

## Essential user requirements
- Three meaningfully distinct suggestions and transparent error states.
- Preserve user intent; optimize response quality within authentic style.
- Equal support for generate and rewrite from the beginning.
- Copy/paste MVP; never falsely imply iMessage integration or auto-send.
- Clear privacy explanation and control before history upload.
- Auth, deletion and tenant isolation prior to real-user private history storage.
- Evaluate actual perceived authenticity against a generic AI baseline.

## Deferred
Autonomous sending, custom keyboard, deep simulated recipient agent, per-user fine-tuning, complex ranking unsupported by evidence.

## Measures
Blind human authenticity preference, goal relevance, naturalness, editing effort, response latency/cost and voluntary retention.

## Open decisions
Exact onboarding/UX mockups, message import formats, pricing, retention defaults and release criteria need reconciliation against the original PRD.
