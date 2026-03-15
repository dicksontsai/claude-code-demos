# Example MCP Servers

A Claude Code plugin with two example MCP servers demonstrating HTTP and stdio transports.

## Servers

### HTTP server with OAuth (`http-server/`)

A Node.js MCP server that implements the full OAuth 2.1 flow. The server acts as both the OAuth authorization server and the MCP resource server — no external auth provider needed.

**How it works:**

1. Claude Code connects to `http://localhost:9876/mcp`
2. The server returns a 401 challenge pointing to its OAuth metadata
3. Claude Code discovers endpoints via `.well-known` metadata, registers a client, and opens your browser
4. You click **Approve** (no password required) and authentication completes
5. Authentication tokens are stored securely and refreshed automatically

**Running:**

```bash
cd http-server
npm install
npm start
```

**OAuth tips:**

* Use "Clear authentication" in the `/mcp` menu to revoke access
* If your browser doesn't open automatically, copy the provided URL and open it manually
* If the browser redirect fails with a connection error after authenticating, paste the full callback URL from your browser's address bar into the URL prompt that appears in Claude Code
* OAuth authentication works with HTTP servers

### stdio server (`stdio-server/`)

A Python MCP server using the low-level SDK (not FastMCP). It runs over stdio so Claude Code manages its lifecycle automatically — no manual server startup needed.

**Prerequisites:** Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — the stdio server uses `uv` to manage its Python environment.

The server includes three example tools designed to be easy to extend:

| Tool | Description |
|------|-------------|
| `greet` | Returns a greeting — simplest possible tool |
| `calculate` | Evaluates arithmetic expressions |
| `get_weather` | Returns mock weather data — swap in a real API |

**Adding a new tool:**

1. Define the tool in the `TOOLS` list (name, description, input schema)
2. Write an async handler function
3. Register it in the `HANDLERS` dict

**Running standalone (for testing):**

```bash
cd stdio-server
uv run python server.py
```

## Plugin installation

```bash
# Install the marketplace (if not already added)
claude plugin marketplace add /path/to/claude-code-demos

# Install this plugin
claude plugin install example-mcps@dickson-cc-demo-plugins
```

After installing, start the HTTP server manually (`cd http-server && npm start`), then use `/mcp` in Claude Code to verify both servers are connected.
