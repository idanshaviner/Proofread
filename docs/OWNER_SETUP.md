# Owner setup and acceptance handoff

Routine offline engineering can continue while these prerequisites are pending.
Never send credentials in chat or commit them. The agent can save cloud drafts,
but cannot enter your secret, apply/publish settings, or access separate ChatGPT
Project conversations. Draft persistence does not prove runtime connectivity.

## Cloud settings

Open this task's cloud environment settings. Review the existing draft rather than
creating a second environment or resetting the live-test budget.

1. Supply the secret requirement `PROOFREAD_OPENAI_API_KEY` with your OpenAI project
   API key. Its only configured destination is `api.openai.com`. Keep
   `PROOFREAD_PROVIDER=mock` and the suggested model `gpt-5.4-mini`.
2. Save/apply the network configuration containing `developer.apple.com`,
   `appleid.apple.com` and `pyjwt.readthedocs.io`. Preserve the other domains.
3. Complete the product's environment publication flow if offered. Tell the agent
   settings were saved; it must recheck actual access and credential presence.

The agent then validates model availability, same-day official compatibility and
prices, and the existing one-time ledger before any inference. The approved
maximum is $2 total once, not a recurring allowance. Missing/copied/unknown ledger
state blocks paid testing; never reset or recreate it to unblock a run.

## Native iOS validation on your Mac

Install Xcode from Apple, launch it once to complete initial setup, and install an
iOS simulator runtime in Xcode settings. Install XcodeGen using its official
instructions (https://github.com/yonaskolb/XcodeGen). No paid hosted runner is needed.
Clone/open this repository, fetch current branches and check out the reviewed PR
branch that includes these changes (`codex/evaluation-output-followups` initially).
From the repository root:

```sh
bash ios/scripts/validate-macos.sh
```

This generates the Xcode project, performs an unsigned simulator build and runs
shared Swift tests. It does not launch the app or prove interactive workflows.
The script's syntax and Linux rejection path were checked here; its macOS build
path remains unexecuted until Xcode actually runs it. Signing is not required for
this simulator build. An Apple signing identity is needed later for device/release.

For interactive acceptance, start the backend in another terminal:

```sh
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PROOFREAD_PROVIDER=mock .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `ios/Proofread.xcodeproj` in Xcode, select the Proofread scheme and an iOS 17+
simulator, then Run. Use invented text only. Verify generate returns three replies,
rewrite preserves the supplied draft in mock form, tapping a suggestion copies its
text, editing input clears stale suggestions, and a stopped backend shows a safe
error. Record Xcode version, simulator/runtime, build result and workflow results;
report failures/logs after reviewing them for secrets. Mock success is not AI quality.

## Finalized requirements

In your ChatGPT Project **Proofread**, open the conversations **AI Communication
Twin PRD**, **Write Technical Specification**, **Brainstorm**, and **Proofread
Development Roadmap**. Export or copy the finalized documents as Markdown into
`docs/source/`, with descriptive filenames and any explicit approved amendments.
Upload the files here or add them through a feature branch/PR. Do not include private
conversation examples or credentials. The agent will reconcile them with current
implementation and ask only about material conflicts.

## Decisions intentionally deferred

Private conversation storage requires a concrete approval proposal for sessions,
consent, retention/deletion and user isolation. Significant UX changes, protected
branch merges and production releases still require owner approval. A macOS GitHub
Actions runner would need a cost/quota decision before enabling it; use the local
Mac path above in the meantime.
