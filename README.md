<div align="center">

# Orchestra

<p align="center">
  <strong>The Persistent Memory & Multi-Agent Orchestration Layer for AI Development</strong>
</p>
<p align="center">
  <a href="https://docs-ebon-xi.vercel.app" target="_blank"><b>Landing Page</b></a> · 
  <a href="https://docs-ebon-xi.vercel.app/manual.html" target="_blank"><b>Official Manual</b></a> · 
  <a href="#quickstart"><b>Quickstart</b></a>
</p>

  <img src="https://img.shields.io/badge/version-3.0.0-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/ecosystem-opencode-purple.svg?style=flat-square" alt="Ecosystem">
  <img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/storage-Git%20%2B%20SQLite%20FTS5-orange.svg?style=flat-square" alt="Storage">
</div>

---

## 🛑 The Pain: Ephemeral AI Amnesia

Every developer building with AI tools faces the same exhausting routine:
1. **Chat Amnesia:** Your session quota expires or you open a fresh chat. Poof—all project context, architecture decisions, and gotchas vanish.
2. **Re-Explaining Overhead:** You spend the first 15 minutes of every chat re-pasting project requirements, tech stack rules, and API endpoints.
3. **Single-Prompt Limitations:** Working on complex features requires manual copy-pasting between separate agent outputs without shared state or testing gates.

## ✨ The Solution: Orchestra

**Orchestra** eliminates chat amnesia by establishing a Git-backed state infrastructure and autonomous agent swarm engine for `opencode`. It gives your AI assistants a persistent, version-controlled brain that lasts across sessions, machines, and quota resets.

---

## 🎯 Features Bound to Developer Pain

| Developer Pain Point | Orchestra Solution | How It Works |
| :--- | :--- | :--- |
| **Lost context on new chats** | 🧠 **Contextual Continuity** | `/handoff` automatically loads project handoffs, the last 3 days of journal entries, and the knowledge base. |
| **Forgetting architectural choices** | 📝 **Immutable Git Brain** | `/remember <fact>` logs decisions into <code>notes.md</code>. Every memory update is git-tracked and fully auditable (`git revert`). |
| **Manual chat session logging** | ⚡ **Auto-Journaling Plugin** | Background TypeScript plugins record raw digests during session idle time. `/done` becomes optional polish. |
| **Managing complex coding tasks** | 🤖 **Multi-Agent Swarm (v3)** | `orchestra run "<goal>"` spawns a hierarchical team of specialized agents (Backend, Frontend, Tester) with automated testing gates. |
| **Fragmented developer tooling** | 📊 **Visual Dashboard** | `orchestra serve` launches a zero-dependency web interface (`:8714`) to audit health, memories, and swarm run boards. |

---

## 🚀 Quickstart

### Installation
Clone the repository and run the setup script to configure your global environment and user PATH:

```powershell
git clone https://github.com/Andres-de-Fonoliousa/orchestra.git
cd orchestra
powershell -ExecutionPolicy Bypass -File install.ps1
```

### The Daily Workflow
| Moment | Command | What happens |
| :--- | :--- | :--- |
| **Starting work** | `/handoff` | Briefs the AI on project state, recent history, and next steps. |
| **Saving a gotcha** | `/remember <fact>` | Permanently logs architectural choices into the knowledge base. |
| **Ending work** | `/done` | Journals session progress, updates handoff notes, and git-commits the brain. |

---

## 🛠️ The CLI Reference

```powershell
orchestra <command> [args]
```

*   `orchestra doctor` — Validates system configuration, memory integrity, and git repo status.
*   `orchestra query "<text>"` — FTS5 natural language search across your entire project history.
*   `orchestra sync` — Pulls, commits, and pushes your memory repo to a private remote.
*   `orchestra serve` — Launches the local visual dashboard interface.
*   `orchestra run "<goal>"` — Initiates a headless multi-agent swarm run.

---

## 📚 Documentation & Resources

- **[Official Manual (v3.0.0)](https://docs-ebon-xi.vercel.app/manual.html)** — Comprehensive guide covering CLI, architecture, plugins, and troubleshooting.
- **[Roadmap](docs/ROADMAP.md)** — Architectural evolution from v1 to v3 swarms.
- **[Contributing Guide](CONTRIBUTING.md)** — Guidelines for building custom plugins and skills.

---

<p align="center">
  <i>Built for the opencode ecosystem. Give your agents a brain that lasts.</i>
</p>
