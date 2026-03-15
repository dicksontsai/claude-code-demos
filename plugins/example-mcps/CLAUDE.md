# Example MCP Servers

Plugin with two example MCP servers: an HTTP server with OAuth and a stdio server.

## Tech stack

- **HTTP server**: Node.js + Express, `@modelcontextprotocol/sdk`
- **stdio server**: Python, `mcp` SDK (low-level API, not FastMCP)

## How to run

HTTP server (must be started manually):

```bash
cd http-server
npm install
npm start
```

The stdio server is managed by Claude Code automatically via the plugin config.

## Guidelines

This is a tutorial project. Keep changes simple and focused.
