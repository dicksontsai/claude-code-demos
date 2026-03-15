# Claude Code HTTP Hooks Dashboard Plugin

A plugin that monitors Claude Code activity in real time via **HTTP hooks** in a dashboard served on localhost:3001.

## What are HTTP hooks?

Claude Code can send HTTP requests to a local server whenever certain events occur during a session. These events include:

- **Tool calls** - When Claude Code invokes a tool (Read, Edit, Bash, etc.)
- **Model responses** - When the model generates a response
- **Notifications** - When Claude Code surfaces a notification

You configure hooks in your Claude Code settings, pointing them at a local URL. Every time the configured event fires, Claude Code POSTs a JSON payload to your server. This lets you build monitoring dashboards, logging pipelines, custom guardrails, and more - all running on your own machine.

## Prerequisites

- **Node.js** (v18 or later recommended)

## Quick start

```bash
# Install dependencies
npm install

# Start the dashboard server
npm start
```

Then open [http://localhost:3001](http://localhost:3001) in your browser.

## Testing without Claude Code

You can send a test event to verify everything works:

```bash
./test-hook.sh
```

This sends a sample `tool_call` payload to the server so you can see it appear on the dashboard.

## Project structure

```
http-hooks-dash/
  server.js           # Express + WebSocket server
  package.json        # Dependencies (express, ws)
  hooks.json          # Sample Claude Code hook configuration
  public/
    index.html        # Dashboard UI (vanilla HTML/CSS/JS)
  test-hook.sh        # Script to send a test event
  CLAUDE.md           # Project context for Claude Code
  README.md           # This file
```
