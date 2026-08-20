---
description: Load the Orchestra brain — current project state, recent journal, and knowledge. Use when starting a new chat or continuing work.
---

This is a fresh session. Recover full context from Orchestra memory instead of asking the user to re-explain anything.

1. Read the project handoff: `./.orchestra/handoff.md`. If it is missing, create `.orchestra/handoff.md` with a summary of this project's AGENTS.md (or your read of the codebase) and its current state.
2. Determine today's date (YYYY-MM-DD), then read `{{HOME}}/.config/opencode/memory/journal/<today>.md` and the previous 2 days' journal entries if present.
3. Read `{{HOME}}/.config/opencode/memory/knowledge/notes.md`.
4. Read `{{HOME}}/.config/opencode/memory/IDENTITY.md` only if you need the user's working preferences.

Present a compact briefing with:

- **Project**: name and what we're building
- **Last session**: what happened (from journal)
- **Current state**: from handoff
- **Next steps**: pending items

Then ask: "Context loaded. What are we working on?" Do not ask the user to re-explain anything already covered by memory.
