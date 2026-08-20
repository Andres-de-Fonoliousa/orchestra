# Orchestra — IDENTITY

This file is loaded into EVERY opencode session (wired via global config `instructions`).
Fill it in once; it is your permanent operating context. Keep it tight — it is read every single session.

## Who am I

- Name: **Yazan** (GitHub: Andres-de-Fonoliousa, email astroid198@gmail.com)
- What I do: Full-stack web developer — web is my specialisation (senior-level skill, ~2-5y experience). Also Python developer + AI automation (bots, scripts). Generalist across security/devops — strong enough to handle, not specialist.
- Current focus / active projects: linkedin_manager (content scheduler MVP); LinkedIn personal-brand push for money: **freelance clients #1, remote/contract work #2, SaaS partnerships #3**. Based in Syria, UTC+3, work remotely.

## How I like to work

- Always plan before editing; detail plans, then execute fast.
- Markdown-first memory via Orchestra (handoff in `.orchestra/`); never re-explain established decisions.
- Ask before destructive operations. No surprises.
- Money-focused and result-focused: no fluff, no stories, no marketing filler.
- Brutal execution speed — 10–11h days when chasing a target; works well under stress.
- Sales skill is low: scripted CTAs and ready-made outreach save him — provide them.

## Stack & conventions

- Web: Laravel (PHP), Vue 3 + Vite + Tailwind, REST APIs, MySQL, Redis (cache + queues), Docker, Ubuntu self-hosting (nginx, backups, zero-downtime deploys).
- Python: async bots (Telegram, aiogram), automation, Tkinter desktop apps, SQLite, APScheduler, requests.
- Deploy: Vercel for static (portfolio); own Ubuntu VPS for products.
- Tools: git/gh, Windows + PowerShell, opencode.
- Commits: short imperative messages; repos private by default.
- LinkedIn content: polished, competent, numbers-driven, bilingual (EN primary ~70%, AR ~30%), zero AI-sounding phrasing, zero emoji, zero "story/opinion" fluff.

## Hard rules

- NEVER commit tokens/secrets. GitHub + Vercel tokens live only in `Desktop\passwords.txt` (use `Get-Content` there when needed).
- NEVER write AI-flavoured marketing copy (no "In today's fast-paced world", "let's dive in", "journey", emoji-clusters). Human dev voice or nothing.
- Never push to GitHub without explicit request; never make repos public without asking.
- Preserve existing code style and conventions when editing.
- End every response with a final line: `Report: <up to 10 words, what was done / the result>`. The voice-report plugin speaks it aloud.

## Maintenance note

- This memory system is built from the `agent_orchistration` project (v2.0.0). Upgrade path: see that project's `docs/ROADMAP.md`.