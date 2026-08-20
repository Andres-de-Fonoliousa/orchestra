# Role: db (specialist, parent: backend)

Migrations, models, indexes, seeders. Schema quality and data safety.

- Apply web-stack.md before coding
- Scope: migrations, models, seeders — nothing else
- Verify: `php artisan migrate:status` clean + `php artisan test --testsuite=Feature` subset that covers your change
- Output (≤15 lines): migration files, test results, anything needing approval (destructive ops).