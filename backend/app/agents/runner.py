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
    """Run an agent: call Claude and the tools until the agent gives its final answer.

    `task` is the task (text) or a conversation already in progress
    ([{"role": "user" | "assistant", "content": ...}, ...], the last message is the user's).
    `allowed_tools` are the MCP server tools the agent may use.
    `local_tools` are tools run here in Python (e.g. the sub agents for the orchestrator),
    in the format {name: {"description", "input_schema", "handler"}}.
    """
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    local_tools = local_tools or {}

    async with connect() as mcp:
        tools = await get_tools(mcp, allowed=allowed_tools)
        # Claude only receives name, description and schema: the handler stays here
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

    raise RuntimeError(f"The agent did not finish within {MAX_TURNS} turns")


async def _execute_tool(mcp, local_tools: dict, name: str, arguments: dict) -> tuple[str, bool]:
    """Run a local tool (a Python function) or, if it is not one, an MCP server tool."""
    if name not in local_tools:
        return await call_tool(mcp, name, arguments)
    try:
        return await local_tools[name]["handler"](**arguments), False
    except Exception as e:
        # Boundary between agents: a sub agent's error becomes an error result
        # for its caller instead of crashing the whole run
        return f"{type(e).__name__}: {e}", True
