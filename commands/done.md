---
description: Save this session to Orchestra memory — journal entry, handoff update, git commit. Run before closing a chat or switching projects.
---

Persist this session's progress now.

1. Determine today's date and current time (YYYY-MM-DD, HH:MM).
2. Append a section to `{{HOME}}/.config/opencode/memory/journal/<YYYY-MM-DD>.md`:

   ### <project-name> — <HH:MM>
   - Done: <bullets of completed work>
   - Decisions: <decisions made and why>
   - Pending: <unfinished items>
   - Open questions: <unresolved items>

3. Update `./.orchestra/handoff.md` (create it if missing) with current state and next steps, keeping it under 40 lines.
4. Commit the memory: run `orchestra commit`. If `orchestra` is not available, fall back to `python "{{HOME}}/.config/opencode/orchestra.py" commit`. If both fail, say so explicitly.
5. Report what was saved and where.
