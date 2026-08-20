# Orchestra Roadmap

Each layer is independent, so upgrades are additive — never rewrites.

## v1.0.0 — done (current)

- [x] Keyring: global config merged at install, tokens set once
- [x] Brain: `IDENTITY.md` auto-loaded, journal, knowledge, per-project handoff
- [x] Handshake: `/handoff`, `/done`, `/remember` global commands
- [x] Helper: `install`, `doctor`, `commit`, `handoff`, `start`, `upgrade`
- [x] Memory folder is its own git repo (undo = git)

Design rules carried forward:

- User data (`IDENTITY.md`, `journal/`, `knowledge/`) is never overwritten by upgrades
- Markdown first, code only where the model is unreliable (timestamps, git)

## v1.1 — polish (folded into v2.0.0)

- [x] `/done` also records a one-line status into the project `AGENTS.md`
- [x] `doctor` warns when `VERSION` in the brain is behind the repo
- [x] Git commit messages auto-tagged with project name

## v2.0 — searchable brain + zero-effort journaling (current)

- [x] **SQLite history layer**: `orchestra.py query "what did we decide about X?"` returns a JSON reply (FTS5). `migrate` rebuilds the index from `journal/` + `knowledge/`; markdown stays the source of truth (SQLite is a derived index, gitignored).
- [x] **Auto-journaling plugin**: opencode TS plugin at `.opencode/plugins/journal.ts` using `message.updated` + `session.idle` hooks writes raw-digest journal entries automatically — `/done` is now optional. Installed to `~/.config/opencode/plugins/`. (Note: `chat.message` no longer exists in opencode 1.18; `experimental.session.compacting` not needed for raw digests.)
- [x] **Voice-report plugin** (bonus, external agent): `voice-report.js` + `tts.ps1` + `notify.ps1` speak the `Report:` line via offline Windows TTS; installed alongside journal.ts, no hook conflicts.
- [x] **Multi-machine sync**: memory repo pushed to a private GitHub remote (`orchestra-memory`); `orchestra sync` = pull --rebase + commit + push. Secrets stay in `opencode.json`, excluded from the brain by design.
- [x] `upgrade` subcommand automated: backup, copy new files, migrate, verify, report.

## v3.0 — swarm: structured agent hierarchy + relentless tester (done, shipped)

- [x] **Skills-first**: `.opencode/skills/` (web-stack, python-bot, deploy-safe, security-scan) — engine embeds playbooks into task cards
- [x] **Role library**: `roles/` — orchestrator (JSON routing), frontend/backend generals + ui/theme/seo/db/api specialists, relentless tester (verdict gate, test-only scope)
- [x] **Swarm engine**: `swarm.py` — `orchestra run/resume/status/runs`, checkpoint+resume (quota-per-chat proof), serial default, 2-retry fix loop → BLOCKED, per-agent git commits
- [x] **Run Board**: `/runs` + `/run?id=` pages, delegation tree, verdict badges, approve/send guidance (POST /run/decision)
- [x] Verify live round-trip: route → execute → tester PASS → done (run #2); FAIL→retry→BLOCKED, resume-after-kill and board-guidance flows implemented but not yet live-tested (quota-costing, follow-up)
- [x] VERSION 3.0.0 + manual chapter

## v3.1 — deferred

## Definition of done for v2.0

1. `orchestra.py doctor` passes after upgrade from v1
2. `orchestra.py query "decisions about X"` returns correct entries from v1-era data
3. A full day of work with zero manual `/done` still produces a complete journal
4. Old chats in v1 format continue to work (no forced migration)