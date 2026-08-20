# Orchestra Manual (v1.0.0)

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
| `serve` | Visual dashboard at http://127.0.0.1:8714 (opens your browser) |
| `commit` | Commit the brain to git (what `/done` calls) |
| `status` | Lists every installed file |
| `start` | Creates `.orchestra/handoff.md` in the current project |
| `handoff [project]` | Deterministic text briefing (works even when the model quota is gone) |
| `upgrade` | Shows current version + what v2.0 will bring |
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

## 7. Upgrading (v1.0.0 → v2.0)

1. Get the newer Orchestra checkout (this project updates in place).
2. `python orchestra.py install <repo path>`
3. `python orchestra.py doctor`

Upgrades never overwrite your data (`IDENTITY.md`, `journal/`, `notes.md`, handoffs).
Backups of the previous config appear as `opencode.jsonc.bak-*` / `opencode.json.bak-*`.
Blueprint: see `docs/ROADMAP.md` (v2.0 = searchable SQLite memory, auto-journaling
plugin, multi-machine sync).

## 8. Troubleshooting

| Problem | Fix |
| --- | --- |
| New chat doesn't know me | Restart opencode (config loads at startup); check `doctor`. |
| `/handoff` says nothing useful | You never ran `/done`; journal is empty — the briefing will still show IDENTITY + knowledge. |
| Config broke, opencode won't start | `OPENCODE_DISABLE_PROJECT_CONFIG=1` then start, fix config, restart. |
| Messed up the brain | The brain is git: `git -C ~/.config/opencode/memory log` → find commit → `git revert`. |
| `serve` port busy | `orchestra serve 9000` (anything above 1024). |
| Handoff/journal look odd on Windows console | The dashboard or `handoff` command display UTF-8 fine; terminal needs UTF-8 (most modern ones do). |
| Where did my old config go | `~/.config/opencode/opencode.jsonc.bak-<timestamp>`. |

## 9. Reference — one-liners

```
/handoff                       # brief me: stack, history, state, next steps
/done                          # save session: journal + handoff + git commit
/remember X                    # permanently store fact X
orchestra serve                # dashboard
orchestra doctor               # health check
orchestra handoff              # text briefing without any model
orchestra commit               # brain -> git now
```