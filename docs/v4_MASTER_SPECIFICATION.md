# Orchestra v4.0.0 Master Specification

## 1. Core Architecture & Modules
- `orchestra.py`: CLI router, server daemon, installer, and diagnostic runner (`orchestra doctor`).
- `swarm.py`: Orchestration engine managing SQLite run states, agent execution, self-healing retries, and event telemetry.
- `dashboard/`: Single-page responsive web dashboard supporting live server mode and standalone offline mode.

## 2. SEO & Web Discoverability
- **Sitemap (`docs/sitemap.xml`):** Lists canonical documentation URLs (`/index.html`, `/MANUAL.md`, `/STRATEGY.md`).
- **Robots.txt (`docs/robots.txt`):** Permits universal crawler indexing (`Allow: /`).
- **Meta Tags:** OpenGraph protocol, Twitter Card, and Googlebot directives in HTML headers.

## 3. Swarm Robustness Protocol
- **Retry Logic:** Maximum 3 attempts per agent step with error injection into prompt history.
- **Data Integrity:** SQLite PRAGMA journal mode WAL for concurrent read/write safety between CLI and web server.

## 4. Release Verification
- Version string updated to `4.0.0` in `VERSION` and `orchestra.py`.
- Automated test suites verified via pytest/unittest.
