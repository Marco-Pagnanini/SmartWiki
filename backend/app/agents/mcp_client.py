"""Ponte tra gli agenti e il server MCP.

Gli agenti non conoscono i tool in anticipo: li chiedono al server MCP,
li convertono nel formato dell'API di Claude e inoltrano le chiamate al server.

Uso tipico dentro un agente:

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
    """Apre una connessione al server MCP e la chiude all'uscita dal blocco `async with`."""
    async with Client(settings.MCP_URL) as client:
        yield client


async def get_tools(client: Client, allowed: list[str] | None = None) -> list[dict[str, Any]]:
    """Restituisce i tool del server nel formato `tools=[...]` dell'API di Claude.

    `allowed` limita i tool a quelli elencati (None = tutti). Un nome in `allowed`
    che il server non ha è quasi sempre un errore di battitura, quindi solleva un errore.
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
            raise ValueError(f"Tool non presenti sul server MCP: {sorted(missing)}")
    return tools


async def call_tool(client: Client, name: str, arguments: dict[str, Any]) -> tuple[str, bool]:
    """Esegue un tool sul server MCP.

    Restituisce (testo del risultato, is_error): sono i due valori che servono
    per costruire il `tool_result` da rimandare al modello.
    """
    result = await client.call_tool(name, arguments)
    text = "\n".join(block.text for block in result.content if block.type == "text")
    return text, bool(result.is_error)
