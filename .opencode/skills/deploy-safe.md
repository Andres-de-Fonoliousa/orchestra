# Skill: deploy-safe.md

Deploy rules for this environment. Read before touching any deployment config.

## Hard rules

- NEVER commit tokens/secrets. GitHub + Vercel tokens live only in `Desktop\passwords.txt`
- Never push to GitHub without explicit request; never make repos public without asking
- Vercel deploys for static sites = manual CLI (`vercel --prod`) with token from passwords.txt; git push never triggers deploy
- Own VPS products: Docker or systemd with `Restart=always`; zero-downtime = build new container/image first, swap after health check

## Zero-downtime checklist

1. `docker compose build` (never `--build` on the live service)
2. Run migrations inside a one-off container BEFORE swapping
3. Health check passes (`curl /health`) on new container before traffic switch
4. Old container stays alive 30s after swap (rollback window)
5. Backups: DB dump before any schema change; keep last 7

## Rollback

- Docker: `docker compose up -d <old-image-tag>` — never delete old images on the same day
- systemd: previous release directory kept one level back

## Output contract

Return: deploy steps run, health check output, rollback instructions, anything that needs a human.