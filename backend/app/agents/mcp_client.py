"""Bridge between the agents and the MCP server.

Agents do not know the tools in advance: they ask the MCP server for them,
convert them to the Claude API format and forward the calls to the server.

Typical use inside an agent:

    async with connect() as client:
        tools = await get_tools(client, allowed=["get_document_by_name"])
        ...
        text, is_error = await call_tool(client, "get_document_by_name", {"name_of_file": "x.pdf"})
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from mcp import Client

from app.core.config import settings


@asynccontextmanager
async def connect() -> AsyncIterator[Client]:
    """Open a connection to the MCP server and close it when the `async with` block exits."""
    async with Client(settings.MCP_URL) as client:
        yield client


async def get_tools(client: Client, allowed: list[str] | None = None) -> list[dict[str, Any]]:
    """Return the server's tools in the `tools=[...]` format of the Claude API.

    `allowed` restricts the tools to the listed ones (None = all). A name in `allowed`
    that the server does not have is almost always a typo, so it raises an error.
    """
    result = await client.list_tools()
    tools = [
        {"name": t.name, "description": t.description or "", "input_schema": t.input_schema}
        for t in result.tools
        if allowed is None or t.name in allowed
    ]
    if allowed is not None:
        missing = set(allowed) - {t["name"] for t in tools}
        if missing:
            raise ValueError(f"Tools not found on the MCP server: {sorted(missing)}")
    return tools


async def call_tool(client: Client, name: str, arguments: dict[str, Any]) -> tuple[str, bool]:
    """Run a tool on the MCP server.

    Return (result text, is_error): the two values needed to build
    the `tool_result` sent back to the model.
    """
    result = await client.call_tool(name, arguments)
    text = "\n".join(block.text for block in result.content if block.type == "text")
    return text, bool(result.is_error)
