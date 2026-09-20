# Orchestra

**The persistent memory and orchestration layer for AI development.**

Orchestra enables seamless context continuity across ephemeral chat sessions. Stop re-pasting project requirements and start building. With git-backed immutable memory and autonomous agent orchestration, your AI assistant finally gets a brain that lasts.

---

### The "Wow" Features

1.  **Contextual Continuity:** Never lose your place. Every new chat session automatically inherits your project's identity, knowledge, and active handoff state.
2.  **Git-Backed Immutable Brain:** Your memory is a verifiable Git repository. Query, search, and audit everything the AI has ever learned about your project.
3.  **Autonomous Agent Swarms:** Go beyond single-prompt engineering. Orchestra orchestrates complex hierarchies of specialized agents (Backend, Frontend, Security, DevOps, Tester) to deliver production-grade features.

---

### Why Orchestra?

AI development tools often suffer from "chat amnesia"—every fresh session requires a fresh prompt. Orchestra solves this by implementing a structured memory bridge that syncs across every chat you start, ensuring the AI behaves like a consistent, long-term team member.

### Quickstart

```bash
# Install Orchestra
powershell -ExecutionPolicy Bypass -File install.ps1

# Start the visual dashboard
orchestra serve
```

*Then, just run `/handoff` in your favorite AI chat.*

---

### Architecture

| Core | Responsibility |
| :--- | :--- |
| **Brain** | Immutable, searchable Git-backed knowledge repository (`~/.config/opencode/memory/`). |
| **Handoff** | Project-specific live state managed through local `.orchestra/` configurations. |
| **Orchestrator** | Hierarchical agent management for complex, multi-step engineering tasks. |

[Documentation](docs/MANUAL.md) · [Roadmap](docs/ROADMAP.md)

---
*Built for the opencode ecosystem.*
