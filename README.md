# Claude Code Tutorial Demos

Companion repo for the Claude Code YouTube tutorial series. Each directory is a self-contained demo — open it in Claude Code to follow along.

## Demos

| Directory | Tutorial Topic | What You'll Build |
|---|---|---|
| [`chrome-extension/`](./chrome-extension/) | Claude Code + Chrome | A full-stack classifieds marketplace app, built interactively with Claude Code and tested live in Chrome |
| [`plugins/http-hooks-dash/`](./plugins/http-hooks-dash/) | HTTP Hooks | A localhost developer dashboard that itself serves as a Claude Code HTTP hook plugin |
| [`plugins/example-mcps/`](./plugins/example-mcps/) | MCP Servers | Example MCP servers — HTTP with OAuth and stdio with Python |
| [`worktrees-demo/`](./worktrees-demo/) | Worktrees | Work on multiple features in parallel using Claude Code's worktrees feature, with Excalidraw as the demo project |

## Plugin Marketplace

This repo doubles as a plugin marketplace, with plugins related to the demos.

```
# Install the marketplace
claude plugin marketplace add ./

# Install a specific plugin
claude plugin install http-hooks-dash@dickson-cc-demo-plugins

# Uninstall the plugin
claude plugin uninstall http-hooks-dash@dickson-cc-demo-plugins

# Remove the marketplace
claude plugin marketplace remove dickson-cc-demo-plugins
```

