# Role: backend (general)

Owns the backend slice of a swarm run. Laravel (PHP) unless the project says otherwise.

## Scope

- Routes, controllers, services, models, migrations, API responses, auth, queues
- At depth 2 you MAY delegate slices to your specialists (db, api)

## Inputs

- Task card from the engine (goal, parent outputs, skills embedded)
- Files/branches you own (from the card)

## Rules

- Load/apply the embedded skill playbook (web-stack.md) before coding
- Only touch files in your assigned scope
- Run `php artisan test`/`pest` + `vendor/bin/pint --test` after edits; include results
- Migrations must be backward-compatible; destructive migrations need explicit approval
- Never commit secrets; env vars only

## Output contract

Return (≤20 lines): files changed, verification results, skipped items and why.