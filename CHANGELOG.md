# Changelog

All notable changes to Orchestra will be documented in this file.

## [3.0.0] — 2026-09-20
### Added
- **v3 Swarm Engine:** Headless multi-agent coding swarms (`orchestra run`) with automated testing gates (`tester-sentinel`) and per-agent git commits.
- **Run Board & Decision API:** Visual dashboard support for monitoring swarm runs (`/runs`, `/run?id=`) with interactive guidance input (`POST /run/decision`).
- **SQLite FTS5 History Layer:** Natural language search across project journals and knowledge bases (`orchestra query`).
- **Auto-Journaling & Voice Plugins:** TypeScript idle-digest journaling plugin and offline Windows TTS voice reporting (`voice-report.js`).
- **Stripe-Grade Landing Page & Docs:** Production-ready Vercel landing page (`docs/index.html`) and Vue-docs styled manual (`docs/manual.html`) featuring Mermaid.js architecture diagrams and scroll-spy navigation.

## [2.0.0] — 2026-08-20
### Added
- Persistent memory brain (`~/.config/opencode/memory/`), identity injection, and global keyring configuration (`opencode.json`).
- Handshake commands: `/handoff`, `/done`, `/remember`.
- Automated brain sync (`orchestra sync`) with private remote.
