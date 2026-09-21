# Orchestra v3.0.0 — The Swarm & Persistence Release

We are thrilled to announce **Orchestra v3.0.0**, a major milestone in persistent AI memory and multi-agent coordination.

## 🚀 What's New in v3.0.0

### 1. Headless Multi-Agent Coding Swarms (`orchestra run`)
- Spawn specialized opencode sessions (`[orchestrator]`, `[backend]`, `[frontend]`, `[tester]`) to plan, build, and test features autonomously.
- Automated testing gatekeeper (`tester-sentinel`) verifies agent output before committing changes to git.
- Interactive Run Board in the visual dashboard to monitor task trees and provide human guidance (`POST /run/decision`).

### 2. SQLite FTS5 History Layer (`orchestra query`)
- High-performance full-text search indexing across all historical project journals and knowledge bases.
- Markdown remains the source of truth, backed by a fast derived SQLite index.

### 3. Auto-Journaling & Voice Plugins
- TypeScript plugin for automated session idle journaling (no manual `/done` required).
- Windows TTS voice reporting (`voice-report.js`) that reads execution outcomes aloud offline.

### 4. Stripe-Grade Landing Page & Vue-Level Documentation
- Production-ready landing page deployed on Vercel with glassmorphism and one-click install copy.
- Official Manual featuring Mermaid.js architecture diagrams, scroll progress bar, and active sidebar Scroll Spy.

---

## 📦 Installation & Upgrade

To install or upgrade to v3.0.0:
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```
*(macOS/Linux: `./install.sh`)*

*Upgrades are fully additive and never overwrite your personal memory brain (`IDENTITY.md`, journals, knowledge).*
