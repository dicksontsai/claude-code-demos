# Dickson's Claude Code Tutorial Demos

Companion repo for my unofficial Claude Code YouTube tutorial series. Each directory is a self-contained demo — open it in Claude Code to follow along. I designed the examples to be overly simple for teaching purposes, not 

## Demos

| Directory | Tutorial Topic | What You'll Build |
|---|---|---|
| [`chrome-extension/`](./chrome-extension/) | Claude Code + Chrome | A toy marketplace webapp, for demonstrating usage of [Claude Chrome Extension with Claude Code](https://code.claude.com/docs/en/chrome#use-claude-code-with-chrome-beta) |
| [`plugins/http-hooks-dash/`](./plugins/http-hooks-dash/) | HTTP Hooks | A localhost dashboard for viewing hook execution, built using HTTP hooks |
| [`plugins/example-mcps/`](./plugins/example-mcps/) | MCP Servers | Example MCP servers — HTTP with OAuth and stdio with Python |
| [`worktrees-demo/`](./worktrees-demo/) | Worktrees | Work on multiple features in parallel using Claude Code's worktrees feature, with Excalidraw as the demo project |
| [`plugins/caveman-output-style/`](./plugins/caveman-output-style/) | Output Styles | A fun caveman output style plugin — few word, result first, grunt good |
| [`plugins/dependency-demo/`](./plugins/dependency-demo/) | Plugin Dependencies | A plugin that depends on another plugin from a [separate marketplace](https://github.com/dicksontsai/plugin-dependency-example) |
| [`plugins/vision-model-skill/`](./plugins/vision-model-skill/) | Skills | A Claude Code plugin port of [anthropic-experimental/vision-model-skill](https://github.com/anthropic-experimental/vision-model-skill) — guides non-technical users from "I want a model that does X" to a working classifier or detector |

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

