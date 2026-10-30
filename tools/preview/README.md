# Current-functionality browser preview

This development harness uses the real FastAPI endpoints, forces mock mode even
if OpenAI is selected in the shell, binds only to loopback and disables access
logs. No private messages, paid calls, persistence, analytics or new native UX.
Generate is fixed; rewrite returns simple draft variations. Neither is AI quality.

From the repository root (or extracted preview bundle), run:

```sh
bash tools/preview/start.command
```

Launcher accepts Python 3.11–3.13; cloud execution is verified on 3.12.
Python 3.15 is not accepted by this launcher because dependency/platform
compatibility has not been validated. Internet is needed on first run to install declared dependencies
into `backend/.venv`. Open http://127.0.0.1:8010 yourself in a local browser. This
is a local testing address, not a hosted cloud preview. Stop with Control-C.
No Xcode, Git or Apple sign-in is required for the extracted bundle.

Try generate, switch to rewrite and change the draft, then copy a suggestion.
Editing inputs clears results and cancels stale requests. Clipboard access depends
on browser permissions; text can be selected/copied manually. Use synthetic text.
The server HTML route and actual generate/rewrite/422 requests were checked in
Linux. Browser rendering, clipboard and Mac launcher execution remain unverified.

## Interpreter selection and recovery

The launcher checks existing Python and dependency versions before starting. It
repairs interrupted dependency installations in a supported environment. It never
deletes or replaces an existing unsupported environment. Choose a separate one:

```sh
PROOFREAD_PYTHON=/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 \
PROOFREAD_VENV=backend/.venv-supported bash tools/preview/start.command
```

Install that interpreter first if absent; use the official macOS downloads list,
not a source-only security-release page. Opening a download page does not install
Python: run the downloaded macOS universal2 `.pkg`. An existing supported environment
is reused; `PROOFREAD_PYTHON` selects Python only when creating a new environment.
Offline launcher regression tests cover selection, preservation and recovery;
the real launcher and API smoke passed on Linux, not on a Mac.
