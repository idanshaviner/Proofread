# Current-functionality browser preview

This development harness uses the real FastAPI endpoints, forces mock mode even
if OpenAI is selected in the shell, binds only to loopback and disables access
logs. No private messages, paid calls, persistence, analytics or new native UX.
Generate is fixed; rewrite returns simple draft variations. Neither is AI quality.

From the repository root (or extracted preview bundle), run:

```sh
bash tools/preview/start.command
```

Requires Python 3.11+ and Internet on first run to install declared dependencies
into `backend/.venv`. Open http://127.0.0.1:8010 yourself in a local browser. This
is a local testing address, not a hosted cloud preview. Stop with Control-C.
No Xcode, Git or Apple sign-in is required for the extracted bundle.

Try generate, switch to rewrite and change the draft, then copy a suggestion.
Editing inputs clears results and cancels stale requests. Clipboard access depends
on browser permissions; text can be selected/copied manually. Use synthetic text.
The server HTML route and actual generate/rewrite/422 requests were checked in
Linux. Browser rendering, clipboard and Mac launcher execution remain unverified.
