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

## v1.1 — polish

- [ ] `/done` also records a one-line status into the project `AGENTS.md` (optional)
- [ ] `doctor` warns when `VERSION` in the brain is behind the repo
- [ ] Git commit messages auto-tagged with project name

## v2.0 — searchable brain + zero-effort journaling

- [ ] **SQLite history layer**: structured memory (project, tags, decisions) with `orchestra.py query "what did we decide about X?"` — the model reads a JSON/SQL reply instead of grepping markdown. Migration is a build script from the existing `journal/` + `knowledge/`, keeping markdown as the source of truth (SQLite is a derived index).
- [ ] **Auto-journaling plugin**: opencode TS plugin using `chat.message` + `experimental.session.compacting` hooks writes journal entries automatically — `/done` becomes optional. Lives at `.opencode/plugin/`, enabled by adding `plugin: ["<repo>/plugin.remote.ts"]` or copying the file in.
- [ ] **Multi-machine sync**: the memory git repo gets a `git remote` (private repo rejection rules: never store keys — secrets stay in `opencode.json`, excluded from the brain by design).
- [ ] `upgrade` subcommand automated: backup, migrate, verify, report.

## v3.0 — integration

- [ ] Memory exposed as an MCP server (`orchestra serve`) so ANY agent tool (opencode, other CLIs, future products) can read/write the brain over the MCP protocol
- [ ] Optional web UI: search memory, browse journal, edit IDENTITY.md
- [ ] Team mode: per-user sections, shared knowledge base

## Definition of done for v2.0

1. `orchestra.py doctor` passes after upgrade from v1
2. `orchestra.py query "decisions about X"` returns correct entries from v1-era data
3. A full day of work with zero manual `/done` still produces a complete journal
4. Old chats in v1 format continue to work (no forced migration)