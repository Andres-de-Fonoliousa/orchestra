# Orchestra Manual (v3.0.0)

Orchestra is your memory layer for opencode. New chats don't remember — Orchestra does.
This manual covers everything: the daily loop, every command, the CLI, the dashboard, and fixes.

## 1. The idea in one diagram

```
chat A (quota used up)          chat B (fresh quota)
        |                              |
   /done saves state              /handoff loads state
        |                              |
        +----------->  THE BRAIN  <----+
   ~/.config/opencode/memory/    (a git repo, undoable)
```

`IDENTITY.md` is loaded into every session automatically (global config `instructions`).
Every chat also has your tokens from the same global config — set once, never again.

## 2. The daily loop (that's all you need)

| Moment | Action |
| --- | --- |
| Starting work (any chat, but especially a fresh one) | `/handoff` |
| Something worth never forgetting | `/remember <fact>` |
| Finished working / quota dying / switching projects | `/done` |

### `/handoff` — "get me up to speed"

Run it in a new chat. The agent reads your project's `.orchestra/handoff.md`,
the last 3 days of journal, and the knowledge base, then presents a briefing:

```
Project: <name> · Last session: <what happened> · Current state: <...> · Next steps: <...>
Context loaded. What are we working on?
```

If no handoff exists yet (first time in a project), the agent creates one.

### `/done` — "save this session"

Run it before closing a chat or when the quota dies. The agent:
1. Appends a dated section to `memory/journal/YYYY-MM-DD.md` (Done / Decisions / Pending / Open questions)
2. Updates `./.orchestra/handoff.md` (current state + next steps, <40 lines)
3. Git-commits the brain: `orchestra commit`

Result: the next chat can resume exactly here.

### `/remember <fact>` — "never lose this"

Appends `**YYYY-MM-DD <project>**: <fact>` to `memory/knowledge/notes.md`.
Use for decisions ("we chose X over Y because Z"), gotchas, conventions, API choices.

## 3. The CLI (`orchestra`)

Install adds `~/.config/opencode` to your user PATH, so from **any new terminal** the
short command works. (New terminals only — a terminal opened before install won't see it yet.)

```powershell
orchestra <command> [args]
```

Fallback for old terminals or if PATH wasn't updated:

```powershell
python "$env:USERPROFILE\.config\opencode\orchestra.py" <command> [args]
```

| Command | What it does |
| --- | --- |
| `doctor` | Checks install: config, memory files, commands, git repo. Exit code 0 = all good. |
| `migrate` | Rebuilds the SQLite search index from journal + knowledge (auto-runs when stale) |
| `query "<text>"` | FTS5 search of the brain — returns structured JSON (project, date, snippet) |
| `sync` | Pull + commit + push the memory repo to its private remote |
| `serve` | Visual dashboard at http://127.0.0.1:8714 (opens your browser) |
| `commit` | Commit the brain to git (what `/done` calls) |
| `status` | Lists every installed file |
| `start` | Creates `.orchestra/handoff.md` in the current project |
| `handoff [project]` | Deterministic text briefing (works even when the model quota is gone) |
| `upgrade [repo]` | Backup the brain, pull new files from a repo checkout, rebuild the index, verify with doctor |
| `install [repo]` | (Re)install/upgrade from a repo checkout; backups old config; never overwrites your data |

Environment: `ORCHESTRA_HOME` overrides the brain location (testing); `ORCHESTRA_NO_BROWSER=1`
prevents `serve` from opening a browser tab.

## 4. The visual dashboard

```powershell
orchestra serve
```

Opens a minimal local page (no internet, no dependencies) showing:
- Health of the install (doctor results, green/red)
- Your `IDENTITY.md` and the knowledge base
- Journal, newest first
- The handoff of the project you launched it from
- One-click **Commit memory** button

Stop it with `Ctrl+C`.

## 5. Tokens & models (once, ever)

Edit `~/.config/opencode/opencode.json`:

```json
{
  "model": "provider/model-id",
  "provider": {
    "my-provider": { "options": { "apiKey": "sk-..." } }
  }
}
```

Prefer env vars so secrets never sit in files:

```json
{ "apiKey": "{env:MY_PROVIDER_KEY}" }
```

Restart opencode after editing (config is read at startup only).

## 6. Per-project state

Each project keeps `.orchestra/handoff.md` (git-ignored in this repo's `.gitignore`).
It's the live "where are we" note. `/handoff` and `/done` read/update it. Delete it and
the next `/handoff` recreates a fresh one from `AGENTS.md` + your journal.

## 7. Upgrading (v1.0.0 → v2.0.0)

1. Get the newer Orchestra checkout (this project updates in place).
2. `python orchestra.py upgrade <repo path>` — backs up the brain, updates files, rebuilds the search index, verifies with `doctor`.
3. Or re-run `python orchestra.py install <repo path>`.

Upgrades never overwrite your data (`IDENTITY.md`, `journal/`, `notes.md`, handoffs).
Backups of the previous config appear as `opencode.jsonc.bak-*` / `opencode.json.bak-*`
and full-brain backups as `opencode-backup-<timestamp>`.

## 8. The auto-journal plugin

v2.0 ships an opencode plugin (`.opencode/plugins/journal.ts`, installed to
`~/.config/opencode/plugins/`) that writes a raw-digest journal entry whenever a
session goes idle — user prompts and assistant replies, clipped. `/done` is now
optional polish on top; a full day of work without `/done` still lands in the
journal. Restart opencode after install to load the plugin.

## 8b. The voice-report plugin

Also ships in `.opencode/plugins/` (from the audio feature): `voice-report.js`
speaks the closing `Report:` line of every assistant reply through Windows TTS
(`tts.ps1`, System.Speech — works offline), shows a rounded toast (`notify.ps1`),
and maps agent roles to distinct voices/rates/sounds. It is additive — it shares
the `session.idle` hook with the journal plugin without interference; hooks run
in sequence.

## 9. Multi-machine sync

The brain is its own git repo with a private remote (`orchestra-memory`).
`orchestra sync` pulls, commits, and pushes. Secrets never enter the brain —
tokens stay in `opencode.json`, which lives outside the memory folder by design.

## 10. Troubleshooting

| Problem | Fix |
| --- | --- |
| New chat doesn't know me | Restart opencode (config loads at startup); check `doctor`. |
| `/handoff` says nothing useful | You never ran `/done`; journal is empty — the briefing will still show IDENTITY + knowledge. |
| Config broke, opencode won't start | `OPENCODE_DISABLE_PROJECT_CONFIG=1` then start, fix config, restart. |
| Messed up the brain | The brain is git: `git -C ~/.config/opencode/memory log` → find commit → `git revert`. |
| `serve` port busy | `orchestra serve 9000` (anything above 1024). |
| Handoff/journal look odd on Windows console | The dashboard or `handoff` command display UTF-8 fine; terminal needs UTF-8 (most modern ones do). |
| Where did my old config go | `~/.config/opencode/opencode.jsonc.bak-<timestamp>`. |

## 12. v3 — the swarm (hierarchical coding agents)

v3 adds a headless agent swarm to Orchestra. One command, and a team of specialized
opencode sessions plans, builds, and tests a feature for you — with a relentless
tester gate and a run board in the dashboard.

### How it works

```
orchestra run "<goal>" --depth 1
        |
   [orchestrator] plans -> task cards (role + spec + skills)
        |
   [frontend] [backend] [ui] [theme] [seo] [db] [api]   <- one agent per card
        |              (each runs as its own headless opencode session)
        |
   [tester]  verifies every agent's work
        |      PASS -> git commit ("swarm run #N <role>: verified by tester")
        |      FAIL -> 2 rework retries, then BLOCKED for your manual decision
        v
   run done -> status + board
```

### Commands

| Command | What it does |
| --- | --- |
| `orchestra run "<goal>" [--depth 1\|2] [--guided]` | Start a swarm run (auto-continue by default) |
| `orchestra status <id>` | Run state + per-agent cards (verdicts, timings, commit refs) |
| `orchestra resume <id>` | Re-run an interrupted run from its saved checkpoint |
| `orchestra runs` | List all runs |

### The board

`orchestra serve` → **Swarm runs board**: every run with status badges, and a
detail page per run showing each agent card with its spec, result, verdict, and
elapsed time. Blocked agents get a decision input — type a correction note,
`POST /run/decision`, and the run resumes with your guidance.

### Rules of the swarm

- Serial execution by default (parallel only when you explicitly opt in).
- Depth ≤ 2: at most two levels of decomposition, ≤ 8 agents per run.
- Every run is checkpointed in `memory/runs.db` — kill it, resume it later.
- Agent work is committed per-agent with the run number, so you can `git log`
  the whole swarm's history and revert any single agent's change.
- Roles live in `roles/` (orchestrator, frontend, backend, ui, theme, seo, db,
  api, tester) and skills in `.opencode/skills/` (web-stack, python-bot,
  deploy-safe, security-scan) — edit them and reinstall.

### Costs & quotas

Each agent = one headless opencode session = quota-consuming. A `--depth 1`
run with 1 task uses ~2 sessions (agent + tester). Plan accordingly.

## 13. Upgrading to v3

1. Get the newer Orchestra checkout (this project updates in place).
2. `python orchestra.py install <repo path>` (or `upgrade`).
3. Restart opencode to load new plugins/skills.

Upgrades never overwrite your data. Your brain, runs, and journals survive.

## 14. Reference — one-liners

```
/handoff                       # brief me: stack, history, state, next steps
/done                          # save session: journal + handoff + git commit
/remember X                    # permanently store fact X
orchestra serve                # dashboard
orchestra doctor               # health check
orchestra handoff              # text briefing without any model
orchestra query "X"            # search the brain (FTS5, JSON out)
orchestra migrate              # rebuild the search index
orchestra sync                 # memory repo -> private remote
orchestra commit               # brain -> git now
orchestra run "goal" --depth 1 # swarm: plan, build, test
orchestra status 3             # run 3 details
orchestra resume 3             # continue a checkpointed run
```