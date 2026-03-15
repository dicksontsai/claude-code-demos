const express = require("express");
const crypto = require("crypto");
const { McpServer } = require("@modelcontextprotocol/sdk/server/mcp.js");
const {
  StreamableHTTPServerTransport,
} = require("@modelcontextprotocol/sdk/server/streamableHttp.js");
const { isInitializeRequest } = require("@modelcontextprotocol/sdk/types.js");
const { z } = require("zod");
const cors = require("cors");

const PORT = process.env.PORT || 9876;
const HOST = process.env.HOST || "localhost";
const SERVER_URL = `http://${HOST}:${PORT}`;

// ---------------------------------------------------------------------------
// In-memory stores for simulated OAuth
// ---------------------------------------------------------------------------
const clients = new Map(); // client_id -> { client_id, client_secret, redirect_uris }
const authCodes = new Map(); // code -> { client_id, redirect_uri, code_challenge, expires }
const accessTokens = new Map(); // token -> { client_id, scope, expires }
const refreshTokens = new Map(); // token -> { client_id, scope }

function randomId() {
  return crypto.randomBytes(24).toString("hex");
}

function tokenExpiresIn() {
  return 3600; // 1 hour
}

// ---------------------------------------------------------------------------
// Express app
// ---------------------------------------------------------------------------
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors({ origin: "*", exposedHeaders: ["Mcp-Session-Id"] }));

// ---------------------------------------------------------------------------
// OAuth: Protected Resource Metadata (RFC 9728)
// ---------------------------------------------------------------------------
app.get("/.well-known/oauth-protected-resource", (_req, res) => {
  res.json({
    resource: SERVER_URL,
    authorization_servers: [SERVER_URL],
    scopes_supported: ["mcp:tools"],
  });
});

// ---------------------------------------------------------------------------
// OAuth: Authorization Server Metadata (RFC 8414)
// ---------------------------------------------------------------------------
app.get("/.well-known/oauth-authorization-server", (_req, res) => {
  res.json({
    issuer: SERVER_URL,
    authorization_endpoint: `${SERVER_URL}/authorize`,
    token_endpoint: `${SERVER_URL}/token`,
    registration_endpoint: `${SERVER_URL}/register`,
    response_types_supported: ["code"],
    grant_types_supported: ["authorization_code", "refresh_token"],
    code_challenge_methods_supported: ["S256"],
    scopes_supported: ["mcp:tools"],
  });
});

// ---------------------------------------------------------------------------
// OAuth: Dynamic Client Registration (RFC 7591)
// ---------------------------------------------------------------------------
app.post("/register", (req, res) => {
  const clientId = randomId();
  const clientSecret = randomId();
  const redirectUris = req.body.redirect_uris || [];

  const client = {
    client_id: clientId,
    client_secret: clientSecret,
    redirect_uris: redirectUris,
    client_name: req.body.client_name || "MCP Client",
    grant_types: req.body.grant_types || ["authorization_code", "refresh_token"],
    response_types: req.body.response_types || ["code"],
  };

  clients.set(clientId, client);
  console.log(`Registered client: ${client.client_name} (${clientId})`);

  res.status(201).json(client);
});

// ---------------------------------------------------------------------------
// OAuth: Authorization endpoint
// Shows a simple "Approve" page — no password required.
// ---------------------------------------------------------------------------
app.get("/authorize", (req, res) => {
  const {
    client_id,
    redirect_uri,
    state,
    code_challenge,
    code_challenge_method,
    scope,
    response_type,
  } = req.query;

  if (response_type !== "code") {
    return res.status(400).send("Unsupported response_type");
  }

  // Render a minimal approval page
  res.type("html").send(`<!DOCTYPE html>
<html>
<head>
  <title>MCP OAuth — Approve Access</title>
  <style>
    body { font-family: system-ui, sans-serif; display: flex; justify-content: center;
           align-items: center; min-height: 100vh; margin: 0; background: #f5f5f5; }
    .card { background: white; padding: 2rem; border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); max-width: 400px; text-align: center; }
    h1 { font-size: 1.4rem; margin-bottom: 0.5rem; }
    p { color: #555; margin-bottom: 1.5rem; }
    .scope { background: #e8f4fd; padding: 0.4rem 0.8rem; border-radius: 6px;
             display: inline-block; font-family: monospace; margin-bottom: 1rem; }
    button { background: #2563eb; color: white; border: none; padding: 0.8rem 2rem;
             border-radius: 8px; font-size: 1rem; cursor: pointer; }
    button:hover { background: #1d4ed8; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Authorize MCP Access</h1>
    <p>An MCP client wants to access this server's tools.</p>
    <div class="scope">${scope || "mcp:tools"}</div>
    <form method="POST" action="/authorize/approve">
      <input type="hidden" name="client_id" value="${client_id || ""}" />
      <input type="hidden" name="redirect_uri" value="${redirect_uri || ""}" />
      <input type="hidden" name="state" value="${state || ""}" />
      <input type="hidden" name="code_challenge" value="${code_challenge || ""}" />
      <input type="hidden" name="code_challenge_method" value="${code_challenge_method || ""}" />
      <input type="hidden" name="scope" value="${scope || "mcp:tools"}" />
      <br />
      <button type="submit">Approve</button>
    </form>
  </div>
</body>
</html>`);
});

// Handle the approval form submission
app.post("/authorize/approve", (req, res) => {
  const { client_id, redirect_uri, state, code_challenge, code_challenge_method, scope } =
    req.body;

  const code = randomId();
  authCodes.set(code, {
    client_id,
    redirect_uri,
    code_challenge,
    code_challenge_method: code_challenge_method || "S256",
    scope: scope || "mcp:tools",
    expires: Date.now() + 5 * 60 * 1000, // 5 minutes
  });

  console.log(`Authorization code issued for client ${client_id}`);

  const redirectUrl = new URL(redirect_uri);
  redirectUrl.searchParams.set("code", code);
  if (state) redirectUrl.searchParams.set("state", state);

  res.redirect(302, redirectUrl.toString());
});

// ---------------------------------------------------------------------------
// OAuth: Token endpoint
// ---------------------------------------------------------------------------
app.post("/token", (req, res) => {
  const { grant_type, code, redirect_uri, code_verifier, refresh_token, client_id, client_secret } =
    req.body;

  if (grant_type === "authorization_code") {
    // Exchange authorization code for tokens
    const authCode = authCodes.get(code);
    if (!authCode) {
      return res.status(400).json({ error: "invalid_grant", error_description: "Invalid authorization code" });
    }
    if (authCode.expires < Date.now()) {
      authCodes.delete(code);
      return res.status(400).json({ error: "invalid_grant", error_description: "Authorization code expired" });
    }

    // Verify PKCE
    if (authCode.code_challenge && code_verifier) {
      const expected = crypto
        .createHash("sha256")
        .update(code_verifier)
        .digest("base64url");
      if (expected !== authCode.code_challenge) {
        return res.status(400).json({ error: "invalid_grant", error_description: "PKCE verification failed" });
      }
    }

    authCodes.delete(code);

    const access = randomId();
    const refresh = randomId();
    const expiresIn = tokenExpiresIn();

    accessTokens.set(access, {
      client_id: authCode.client_id,
      scope: authCode.scope,
      expires: Date.now() + expiresIn * 1000,
    });
    refreshTokens.set(refresh, {
      client_id: authCode.client_id,
      scope: authCode.scope,
    });

    console.log(`Access token issued for client ${authCode.client_id}`);

    return res.json({
      access_token: access,
      refresh_token: refresh,
      token_type: "Bearer",
      expires_in: expiresIn,
      scope: authCode.scope,
    });
  }

  if (grant_type === "refresh_token") {
    const stored = refreshTokens.get(refresh_token);
    if (!stored) {
      return res.status(400).json({ error: "invalid_grant", error_description: "Invalid refresh token" });
    }

    // Rotate tokens
    refreshTokens.delete(refresh_token);

    const newAccess = randomId();
    const newRefresh = randomId();
    const expiresIn = tokenExpiresIn();

    accessTokens.set(newAccess, {
      client_id: stored.client_id,
      scope: stored.scope,
      expires: Date.now() + expiresIn * 1000,
    });
    refreshTokens.set(newRefresh, {
      client_id: stored.client_id,
      scope: stored.scope,
    });

    console.log(`Token refreshed for client ${stored.client_id}`);

    return res.json({
      access_token: newAccess,
      refresh_token: newRefresh,
      token_type: "Bearer",
      expires_in: expiresIn,
      scope: stored.scope,
    });
  }

  res.status(400).json({ error: "unsupported_grant_type" });
});

// ---------------------------------------------------------------------------
// Bearer auth middleware for MCP endpoints
// ---------------------------------------------------------------------------
function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    res.set(
      "WWW-Authenticate",
      `Bearer realm="mcp", resource_metadata="${SERVER_URL}/.well-known/oauth-protected-resource"`
    );
    return res.status(401).json({ error: "unauthorized" });
  }

  const token = authHeader.slice(7);
  const stored = accessTokens.get(token);
  if (!stored) {
    res.set(
      "WWW-Authenticate",
      `Bearer realm="mcp", resource_metadata="${SERVER_URL}/.well-known/oauth-protected-resource"`
    );
    return res.status(401).json({ error: "invalid_token" });
  }

  if (stored.expires < Date.now()) {
    accessTokens.delete(token);
    res.set(
      "WWW-Authenticate",
      `Bearer realm="mcp", resource_metadata="${SERVER_URL}/.well-known/oauth-protected-resource"`
    );
    return res.status(401).json({ error: "invalid_token", error_description: "Token expired" });
  }

  req.auth = stored;
  next();
}

// ---------------------------------------------------------------------------
// MCP Server setup
// ---------------------------------------------------------------------------
const transports = {};

function createMcpServer() {
  const server = new McpServer({
    name: "example-http-oauth",
    version: "1.0.0",
  });

  server.registerTool(
    "run_query",
    {
      title: "Run Query",
      description: "Executes a query against a simulated database and returns matching rows. Available tables: users (id, name, age, department), orders (id, user_id, product, amount, status), products (id, name, price, stock, category)",
      inputSchema: {
        query: z.string().describe("SQL-like query string, e.g. SELECT * FROM users WHERE age > 30"),
      },
    },
    async ({ query }) => {
      const datasets = {
        users: [
          { id: 1, name: "Alice",   age: 32, department: "Engineering" },
          { id: 2, name: "Bob",     age: 27, department: "Marketing"   },
          { id: 3, name: "Carol",   age: 45, department: "Engineering" },
          { id: 4, name: "Dave",    age: 22, department: "Design"      },
          { id: 5, name: "Eve",     age: 38, department: "Engineering" },
        ],
        orders: [
          { id: 101, user_id: 1, product: "Laptop",  amount: 1299.99, status: "shipped"   },
          { id: 102, user_id: 2, product: "Mouse",   amount:   29.99, status: "delivered" },
          { id: 103, user_id: 1, product: "Monitor", amount:  499.99, status: "pending"   },
          { id: 104, user_id: 3, product: "Keyboard",amount:   89.99, status: "delivered" },
          { id: 105, user_id: 5, product: "Headset", amount:  149.99, status: "shipped"   },
        ],
        products: [
          { id: 1, name: "Laptop",   price: 1299.99, stock: 42, category: "Electronics" },
          { id: 2, name: "Mouse",    price:   29.99, stock: 210, category: "Peripherals" },
          { id: 3, name: "Monitor",  price:  499.99, stock: 18, category: "Electronics" },
          { id: 4, name: "Keyboard", price:   89.99, stock: 95, category: "Peripherals" },
          { id: 5, name: "Headset",  price:  149.99, stock: 63, category: "Peripherals" },
        ],
      };

      const lower = query.toLowerCase();
      let table = null;
      for (const name of Object.keys(datasets)) {
        if (lower.includes(name)) {
          table = name;
          break;
        }
      }

      const rows = table ? datasets[table] : [];
      const result = {
        query,
        table: table || "(unknown)",
        row_count: rows.length,
        rows,
      };

      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    }
  );

  return server;
}

// MCP POST handler (Streamable HTTP)
async function mcpPostHandler(req, res) {
  const sessionId = req.headers["mcp-session-id"];
  let transport;

  if (sessionId && transports[sessionId]) {
    transport = transports[sessionId];
  } else if (!sessionId && isInitializeRequest(req.body)) {
    transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => crypto.randomUUID(),
      onsessioninitialized: (sid) => {
        transports[sid] = transport;
      },
    });

    transport.onclose = () => {
      if (transport.sessionId) {
        delete transports[transport.sessionId];
      }
    };

    const server = createMcpServer();
    await server.connect(transport);
  } else {
    return res.status(400).json({
      jsonrpc: "2.0",
      error: { code: -32000, message: "Bad Request: No valid session ID" },
      id: null,
    });
  }

  await transport.handleRequest(req, res, req.body);
}

// MCP GET/DELETE handler
async function mcpSessionHandler(req, res) {
  const sessionId = req.headers["mcp-session-id"];
  if (!sessionId || !transports[sessionId]) {
    return res.status(400).send("Invalid or missing session ID");
  }
  await transports[sessionId].handleRequest(req, res);
}

// Apply auth and register MCP routes
app.post("/mcp", requireAuth, mcpPostHandler);
app.get("/mcp", requireAuth, mcpSessionHandler);
app.delete("/mcp", requireAuth, mcpSessionHandler);

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
app.listen(PORT, HOST, () => {
  console.log(`MCP HTTP server with OAuth running at ${SERVER_URL}`);
  console.log(`MCP endpoint: ${SERVER_URL}/mcp`);
  console.log(`OAuth metadata: ${SERVER_URL}/.well-known/oauth-authorization-server`);
  console.log();
  console.log("No password required — just click Approve in the browser.");
});
