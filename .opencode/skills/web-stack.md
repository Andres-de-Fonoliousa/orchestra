# Skill: web-stack.md

Laravel (PHP) + Vue 3 + Vite + Tailwind + REST + MySQL + Redis (cache/queues) + Docker + Ubuntu self-hosting.

## Verification commands (run BEFORE claiming done)

- PHP: `vendor/bin/pint --test` (style), `php artisan test` or `pest` (suite)
- Frontend: `npm run lint`, `npm run test` or `vitest run`
- Build: `npm run build` must pass; Vite warnings are OK, errors are not
- Migrations: `php artisan migrate:status` clean; never run destructive migrations without explicit approval

## Conventions

- Controllers thin, services hold logic; Form Requests for validation; API resources for responses
- DB: migrations + models with fillable guarded; never raw SQL in controllers
- Redis: cache for reads, queue for jobs (sync driver only in local dev)
- Error handling: HTTP exceptions mapped to JSON, never leak stack traces
- Auth: Laravel Sanctum; policies not role checks scattered in views
- Frontend: Composition API, `<script setup>`, TypeScript unless project says otherwise; Tailwind classes, no inline CSS blobs; components in `src/components/` PascalCase

## Gotchas (from Orchestra knowledge)

- `.env` is never committed; `env:VAR` refs only
- Zero-downtime deploy: nginx + php-fpm restart order matters (see deploy-safe.md)
- UTF-8: PowerShell writes need `-Encoding utf8`; Python console needs `PYTHONIOENCODING=utf-8` (cp1256 kills non-ASCII)

## Output contract

Return: files changed, test results (commands + pass counts), anything left for the tester.