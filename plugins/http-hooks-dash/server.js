const express = require("express");
const http = require("http");
const { WebSocketServer } = require("ws");
const path = require("path");

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

const PORT = 3001;
const startTime = Date.now();

// In-memory event store
let events = [];

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

// ── POST /hooks ── receive Claude Code HTTP hook payloads ──────────────
app.post("/hooks", (req, res) => {
  const event = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
    receivedAt: new Date().toISOString(),
    ...req.body,
  };

  events.unshift(event);

  // Broadcast to all connected WebSocket clients
  const message = JSON.stringify({ type: "new_event", event });
  wss.clients.forEach((client) => {
    if (client.readyState === 1) {
      client.send(message);
    }
  });

  res.json({ ok: true });
});

// ── GET /api/events ── retrieve stored events ─────────────────────────
app.get("/api/events", (_req, res) => {
  res.json(events);
});

// ── GET /api/stats ── aggregate statistics ─────────────────────────────
app.get("/api/stats", (_req, res) => {
  const byType = {};
  const overTime = {};

  events.forEach((e) => {
    // Count by type
    const t = e.type || "unknown";
    byType[t] = (byType[t] || 0) + 1;

    // Count by minute bucket
    const minute = (e.receivedAt || e.timestamp || "").slice(0, 16); // YYYY-MM-DDTHH:MM
    if (minute) {
      overTime[minute] = (overTime[minute] || 0) + 1;
    }
  });

  const sessions = new Set(events.map((e) => e.session_id).filter(Boolean));

  res.json({
    total: events.length,
    byType,
    overTime,
    totalSessions: sessions.size,
  });
});

// ── DELETE /api/events ── clear the log ────────────────────────────────
app.delete("/api/events", (_req, res) => {
  const count = events.length;
  events = [];

  // Notify all WebSocket clients
  const message = JSON.stringify({ type: "events_cleared" });
  wss.clients.forEach((client) => {
    if (client.readyState === 1) {
      client.send(message);
    }
  });

  res.json({ ok: true, cleared: count });
});

// ── WebSocket ──────────────────────────────────────────────────────────
wss.on("connection", (ws) => {
  // Send current event count on connect
  ws.send(JSON.stringify({ type: "connected", eventCount: events.length }));
});

// ── Start ──────────────────────────────────────────────────────────────
server.listen(PORT, () => {
  console.log(`Dashboard running at http://localhost:${PORT}`);
  console.log(`Hook endpoint:       POST http://localhost:${PORT}/hooks`);
  console.log(`\nWaiting for Claude Code events...`);
});
