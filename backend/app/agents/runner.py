from anthropic import AsyncAnthropic

from app.agents.mcp_client import call_tool, connect, get_tools
from app.core.config import settings

MAX_TURNS = 10


async def run_agent(
    system_prompt: str,
    allowed_tools: list[str],
    task: str | list[dict],
    local_tools: dict | None = None,
) -> str:
    """Esegue un agente: chiama Claude e i tool finché l'agente non dà la risposta finale.

    `task` è il compito (testo) oppure una conversazione già iniziata
    ([{"role": "user" | "assistant", "content": ...}, ...], l'ultimo messaggio è dell'utente).
    `allowed_tools` sono i tool del server MCP che l'agente può usare.
    `local_tools` sono tool eseguiti qui in Python (es. i sub agenti per l'orchestrator),
    nel formato {nome: {"description", "input_schema", "handler"}}.
    """
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    local_tools = local_tools or {}

    async with connect() as mcp:
        tools = await get_tools(mcp, allowed=allowed_tools)
        # A Claude si mandano solo nome, descrizione e schema: l'handler resta qui
        tools += [
            {"name": name, "description": tool["description"], "input_schema": tool["input_schema"]}
            for name, tool in local_tools.items()
        ]
        messages = list(task) if isinstance(task, list) else [{"role": "user", "content": task}]

        for _ in range(MAX_TURNS):
            response = await client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                output_config={"effort": settings.ANTHROPIC_EFFORT},
                system=system_prompt,
                tools=tools,
                messages=messages,
                max_tokens=2000,
            )
            if response.stop_reason != "tool_use":
                return "".join(block.text for block in response.content if block.type == "text")

            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    text, is_error = await _execute_tool(mcp, local_tools, block.name, block.input)
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": text,
                        "is_error": is_error,
                    })
            messages.append({"role": "user", "content": results})

    raise RuntimeError(f"L'agente non ha finito entro {MAX_TURNS} turni")


async def _execute_tool(mcp, local_tools: dict, name: str, arguments: dict) -> tuple[str, bool]:
    """Esegue un tool locale (funzione Python) oppure, se non lo è, un tool del server MCP."""
    if name not in local_tools:
        return await call_tool(mcp, name, arguments)
    try:
        return await local_tools[name]["handler"](**arguments), False
    except Exception as e:
        # Confine tra agenti: l'errore di un sub agente diventa un risultato di errore
        # per chi lo ha chiamato, invece di far cadere l'intera esecuzione
        return f"{type(e).__name__}: {e}", True
