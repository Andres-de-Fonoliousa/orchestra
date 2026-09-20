# Contributing Plugins to Orchestra

Orchestra is designed to be extensible. You can add custom functionality by dropping scripts into the `plugins/` directory of your Orchestra installation.

## Plugin Lifecycle

1.  **Placement:** Place your script in `~/.config/opencode/plugins/`.
2.  **Registration:** Plugins are automatically discovered at startup by the `orchestra` core.
3.  **Hooks:** Plugins hook into Orchestra's lifecycle events (e.g., `chat.message` - though this is deprecated, use `message.updated` + `session.idle` for auto-journaling).

## Supported File Types
Orchestra currently supports:
- TypeScript (`.ts`) - Validated via `bun build`.
- JavaScript (`.js`)
- PowerShell scripts (`.ps1`)

## Plugin Best Practices
- **Idempotency:** Plugins should be able to run multiple times without causing side effects.
- **Asynchronicity:** For long-running tasks, ensure your plugin handles async operations properly to avoid blocking the main Orchestra loop.
- **Error Handling:** Plugins should fail gracefully. Use logging where appropriate.

## Creating a New Plugin
1.  Create a new file in `plugins/`.
2.  If it's a TS plugin, ensure it can be bundled by the `bun build` process.
3.  Test your plugin using the `orchestra serve` dashboard to ensure it is correctly registered.
