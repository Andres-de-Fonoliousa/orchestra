# Contributing to Orchestra

Welcome! We are excited to have you contribute to Orchestra. Whether you are improving the visual dashboard, building a new plugin, or perfecting the memory indexer, your help is appreciated.

## How to Contribute

1.  **Fork** the repository.
2.  **Create** a branch for your feature: `git checkout -b feature/amazing-new-capability`.
3.  **Implement** your changes.
4.  **Run** the doctor to ensure your setup is valid: `python orchestra.py doctor`.
5.  **Commit** with a clear message.
6.  **Push** to your fork and submit a **Pull Request**.

## Contribution Areas

### Plugins (`.opencode/plugins/`)
Orchestra is designed for extensibility. We welcome new plugins that enhance session journaling, reporting, or automation. Check existing plugins for the required hook structure.

### Skills (`.opencode/skills/`)
Help us build a robust library of skills for common engineering tasks (e.g., `web-stack`, `python-bot`, `security-scan`). Skills must include a formal `SKILL.md` with clear triggers.

### Visualizer (Web Dashboard)
Help us improve the local memory dashboard! We are currently transitioning to a Tailwind/Vue 3 stack.

## Questions?
Check `docs/MANUAL.md` for the technical reference. If you're stuck, open an issue!
