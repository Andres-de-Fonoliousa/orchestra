# Skill: python-bot.md

Async Python bots (aiogram/PTB), automation, Tkinter apps, SQLite, APScheduler, requests.

## Verification commands (run BEFORE claiming done)

- Tests: `pytest -q` — all pass before you finish
- Import smoke: `python -m app.main` must not crash on import (watch for circular imports)
- Style: `python -m py_compile <files>` for syntax; ruff if the project uses it

## Conventions

- Entry point: always `python -m app.main`, never `python app/main.py` (imports break)
- PTB 21.x: no `context.application.to_thread` — use `await asyncio.to_thread(...)` (import asyncio)
- Jobs/scheduler: APScheduler or PTB JobQueue; wrap sync calls in `asyncio.to_thread`
- DB: SQLite via SQLAlchemy or sqlite3; run migrations AFTER model imports (`create_all` on empty models = zero tables)
- Secrets: only via `.env` (gitignored); tokens never in code or logs
- Long-running bots: systemd or Docker with restart=always; logs to files, not stdout-only

## Gotchas (from Orchestra knowledge)

- Idempotency: order/payment handlers must be replay-safe (dedupe by order_uuid)
- Never force-kill long-running processes on this machine without a graceful path first
- Windows console: set `PYTHONIOENCODING=utf-8` before printing non-ASCII

## Output contract

Return: files changed, test results (pytest count + failures), migration state, anything left for the tester.