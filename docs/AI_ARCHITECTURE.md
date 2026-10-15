# Personalization research hypothesis — provisional
Do not confuse this summary with the previously completed architecture research.

1. Obtain user permission; distinguish user's outgoing messages from others' messages.
2. Extract editable style traits: case, punctuation, emoji, humor, slang, length and social register.
3. Combine immediate message, relationship, conversation context and explicit goal.
4. Optionally retrieve a few relevant authorized examples (strict per-user isolation).
5. Generate structured, diverse suggestions for both compose and rewrite using a hosted model.
6. Validate structure, distinctness, goal fidelity and fit to style. Rank only if evaluation proves gains.
7. Use explicit choices and edits for progressive learning; support erasure and correction.

**Evaluation:** compare generic LLM, simple style instructions, structured profile, profile+retrieval and final pipeline on consented/synthetic scenarios. Human blind ratings (authenticity, helpfulness, intent preservation) plus edit effort, p95 latency and cost. No proof of superiority until measured.

Avoid premature fine-tuning, recipient digital-twin simulation and elaborate agent orchestration.
