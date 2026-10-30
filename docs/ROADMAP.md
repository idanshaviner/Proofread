# Working roadmap — owner keyboard update

October 30 owner requirement supersedes the previous indefinite keyboard deferral.
Original PRD/SPEC/research exports remain outstanding. See
[source requirement](source/KEYBOARD_REQUIREMENT_2026-10-30.md) and
[proposed architecture and gates](KEYBOARD_PROPOSAL.md).

| Phase | Objective | Required exit evidence |
| --- | --- | --- |
| Prerequisite | Approved identity/privacy/import design before private history; synthetic work can continue | Consent, deletion and isolation design; verified platform feasibility and actual Xcode capability |
| 1 | Personalization foundation: message import, editable writing and relationship profiles | Approved data handling; authorship/isolation/deletion tests; meaningful profile validation |
| 2 | Shared AI generate/rewrite with context | Real-model and native acceptance, intent/authenticity assessment versus generic baseline, approved budget |
| 3 | Cross-app custom keyboard prototype | Approved own-keyboard UI, permission states, shared backend and explicit insertion; device lifecycle/proxy tests |
| 4 | Cross-application verification | Observed app/iOS/version compatibility matrix and documented restrictions/fallbacks |
| 5 | Personal daily-use validation | Privacy/auth/budget gates met; explicit feedback, latency and usefulness evidence |
| 6 | Refinement and broader release | Keyboard ergonomics/accessibility, quality/cost/security/review gates and separate release approval |

The owner approved a small synthetic platform spike; see
`KEYBOARD_PROTOTYPE_TESTING.md` for its offline implementation and native validation
gates. It de-risks Phase 3 without authorizing private imports or superseding the
owner's phase priorities. App-store/provider spending, storage/retention, final
keyboard UI and architecture changes remain approval-bound. Current prototype
code remains working; this roadmap is direction, not a completion claim.
