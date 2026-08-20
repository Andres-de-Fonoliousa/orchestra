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
- [x] **Multi-machine sync**: memory repo pushed to a private GitHub remote (`orchestra-memory`); `orchestra sync` = pull --rebase + commit + push. Secrets stay in `opencode.json`, excluded from the brain by design.
- [x] `upgrade` subcommand automated: backup, copy new files, migrate, verify, report.

## v3.0 — integration

- [ ] Memory exposed as an MCP server (`orchestra serve`) so ANY agent tool (opencode, other CLIs, future products) can read/write the brain over the MCP protocol
- [ ] Optional web UI: search memory, browse journal, edit IDENTITY.md
- [ ] Team mode: per-user sections, shared knowledge base

## Definition of done for v2.0

1. `orchestra.py doctor` passes after upgrade from v1
2. `orchestra.py query "decisions about X"` returns correct entries from v1-era data
3. A full day of work with zero manual `/done` still produces a complete journal
4. Old chats in v1 format continue to work (no forced migration)