# Orchestra

Opencode session orchestration. One brain, every chat. No token repasting, no context re-explaining.

Read the full usage manual first: **`docs/MANUAL.md`**. Try the visual dashboard after install:
`orchestra serve` (opens a local page with your memory, health, and a commit button — run it in a NEW terminal).

## The problem it solves

Your free opencode limit is per chat. New chat = fresh quota, but also = amnesia. Orchestra makes every new chat pick up exactly where the last one left off.

## How it works

Three layers:

| Layer | What | Where |
| --- | --- | --- |
| Keyring | tokens, model, config set once, inherited by every chat | `~/.config/opencode/opencode.json` |
| Brain | permanent memory every session reads | `~/.config/opencode/memory/` |
| Handshake | 3 commands that bridge chats | global commands `/handoff` `/done` `/remember` |

## Install (2 minutes)

```
cd <this project folder>
powershell -ExecutionPolicy Bypass -File install.ps1
```

Or manually: `python orchestra.py install <repo path>` then `python orchestra.py doctor`.

Then **quit and restart opencode** (config loads only at startup), and fill in
`~/.config/opencode/memory/IDENTITY.md` once — it is loaded into every session.

## Daily use

| When | What |
| --- | --- |
| Hitting the limit / rotating chats | New chat, run `/handoff`, paste-back the briefing is automatic |
| Ending a session | `/done` — journals the session, updates handoff, git-commits the brain |
| A fact worth never forgetting | `/remember <fact>` |
| Deterministic fallback (no quota) | `orchestra handoff` (in a new terminal) |
| Visual dashboard | `orchestra serve` |

## Adding a model or token

Edit `~/.config/opencode/opencode.json` — one file, one time. Example:

```json
{
  "model": "provider/model-id",
  "provider": { "provider-name": { "options": { "apiKey": "sk-..." } } }
}
```

For keys, you can also use env vars: `"apiKey": "{env:MY_KEY}"` keeps secrets out of the file.

## Layout

```
~/.config/opencode/
  opencode.json          # Keyring (merged, your config preserved)
  orchestra.py           # helper: doctor / commit / handoff / upgrade
  VERSION
  commands/              # handoff.md, done.md, remember.md
  memory/                # THE BRAIN — its own git repo
    IDENTITY.md          # who you are (read into every session)
    journal/YYYY-MM-DD.md  # session diary
    knowledge/notes.md   # lasting facts
<your-project>/.orchestra/handoff.md   # live per-project state
```

## Troubleshooting

- **Nothing changed after install** → restart opencode; config is not hot-reloaded.
- **Broken config, opencode won't start** → `OPENCODE_DISABLE_PROJECT_CONFIG=1` skips project config; fix and restart.
- **Memory edit went wrong** → the brain is a git repo: `git -C ~/.config/opencode/memory log` to undo.
- **Backup of your old config** → look for `opencode.jsonc.bak-*` in `~/.config/opencode/`.

## Upgrades

Version is tracked (`VERSION`). Re-run the installer from a newer checkout to
upgrade — user data (`IDENTITY.md`, `journal/`, `notes.md`) is never overwritten.
`orchestra upgrade <repo path>` automates it: backup, file update, index rebuild,
doctor verification. v3.0 blueprint: `docs/ROADMAP.md`.