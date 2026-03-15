"""
Example stdio MCP server using the low-level Python SDK.

This server demonstrates how to build an MCP server without FastMCP,
giving you full control over the protocol. It's designed to be easy
to extend — just add new tools following the patterns below.

Run directly:
    uv run server.py

Or with python (after installing deps):
    pip install mcp
    python server.py
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

# Use stderr for logging — stdout is reserved for MCP JSON-RPC messages.
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool definitions
#
# To add a new tool:
#   1. Define it in TOOLS (name, description, inputSchema)
#   2. Add a handler function
#   3. Register it in the HANDLERS dict
# ---------------------------------------------------------------------------

TOOLS: list[types.Tool] = [
    types.Tool(
        name="greet",
        description="Returns a friendly greeting for the given name.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name to greet",
                },
            },
            "required": ["name"],
        },
    ),
    types.Tool(
        name="calculate",
        description=(
            "Evaluates a basic arithmetic expression. "
            "Supports +, -, *, / and parentheses."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": 'Arithmetic expression, e.g. "(2 + 3) * 4"',
                },
            },
            "required": ["expression"],
        },
    ),
    types.Tool(
        name="get_weather",
        description=(
            "Returns mock weather data for a city. "
            "Replace the implementation with a real API call to make it useful."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name",
                },
            },
            "required": ["city"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


async def handle_greet(arguments: dict) -> list[types.TextContent]:
    name = arguments.get("name", "World")
    return [types.TextContent(type="text", text=f"Hello, {name}!")]


async def handle_calculate(arguments: dict) -> list[types.TextContent]:
    expression = arguments.get("expression", "")

    # Only allow safe characters for arithmetic
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return [
            types.TextContent(
                type="text",
                text=f"Error: expression contains invalid characters. Only digits and +-*/() are allowed.",
            )
        ]

    try:
        result = eval(expression)  # safe: input is restricted to arithmetic chars
        return [types.TextContent(type="text", text=f"{expression} = {result}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error evaluating expression: {e}")]


async def handle_get_weather(arguments: dict) -> list[types.TextContent]:
    city = arguments.get("city", "Unknown")
    # Mock data — swap this out for a real weather API.
    mock = {
        "city": city,
        "temperature_f": 72,
        "condition": "Partly cloudy",
        "humidity_pct": 45,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return [types.TextContent(type="text", text=json.dumps(mock, indent=2))]


# Map tool names to handler functions.
HANDLERS = {
    "greet": handle_greet,
    "calculate": handle_calculate,
    "get_weather": handle_get_weather,
}

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

app = Server("example-stdio")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return TOOLS


@app.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    handler = HANDLERS.get(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")
    return await handler(arguments)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main():
    logger.info("Starting example-stdio MCP server")
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
