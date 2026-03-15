# Claude Code HTTP Hooks Dashboard

Developer dashboard for monitoring Claude Code activity via HTTP hooks.

## Dual purpose

This project is both a tutorial walkthrough and a functional HTTP hook plugin. When the server is running, it receives real hook payloads from Claude Code and displays them in a live dashboard.

## Tech stack

- **Server**: Express (Node.js)
- **Real-time**: WebSocket (ws library)
- **Frontend**: Vanilla HTML, CSS, and JavaScript - no frameworks

## How to run

```bash
npm install
npm start
```

The dashboard is available at http://localhost:3001.

## How to install as a plugin

```bash
claude plugin install /path/to/http-hooks
```

This automatically configures the HTTP hooks in your Claude Code settings via `hooks/hooks.json`. No manual configuration needed.

To test locally before installing:

```bash
claude --plugin-dir .
```

## API endpoints

- `POST /hooks` - Receives Claude Code HTTP hook payloads
- `GET /api/events` - Returns all stored events
- `GET /api/stats` - Returns aggregate stats (total count, by type, over time)
- `DELETE /api/events` - Clears the event log

WebSocket connections are available on the same port for real-time event streaming.

## Guidelines

This is a tutorial project. Keep changes simple and focused.
