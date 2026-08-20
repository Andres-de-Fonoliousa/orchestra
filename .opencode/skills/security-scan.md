# Skill: security-scan.md

Security audit playbook. Run after any code changes that touch auth, payments, tokens, or public surfaces.

## Scan checklist

1. **Secrets**: grep for `sk-`, `ghp_`, `token`, `password` in code/tests/docker — anything real must move to `.env`/env vars. `.env` must be gitignored
2. **History**: if a secret was ever committed: `git-filter-repo` purge + force-push, then verify `git log -p` shows nothing (token may be in reflog/CI caches — rotate it anyway)
3. **Auth**: rate limits on login; hashed access codes; no hardcoded admin IDs
4. **Payments/refunds**: refund handler idempotent (dedupe by refund uuid); double-credit guard on deposits
5. **CSRF/XSS**: forms have CSRF tokens; user input escaped on render; no `innerHTML` with unsanitized data
6. **Exposure**: no stack traces to clients; error messages generic; debug endpoints off in prod

## Output contract

Return: checklist table (item / status / evidence), list of real findings with severity, recommended fix per finding.