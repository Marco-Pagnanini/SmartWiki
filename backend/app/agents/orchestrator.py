from app.agents import researcher, wiki
from app.agents.runner import run_agent

SYSTEM_PROMPT = """You are the assistant of SmartWiki, a company wiki of documents.
You talk with the user and coordinate two agents, available as tools:
- ask_researcher: finds a document by its exact file name. It can only read.
- ask_archivist: adds a new document (unique file name, group number >= 1, optional summary).
  It can only create.
You cannot read or change the wiki yourself: everything about documents goes through these agents.

How to work:
- Decide which agent the request needs. A request can need both, one after the other
  (for example: check whether a document exists, then add it).
- The agents cannot see this conversation. Every task you send must be complete and
  self-contained: always repeat the exact file name, group number and summary to use,
  never write things like "add it" or "the same document".
- Before asking the archivist to add a document, make sure the user gave the file name and
  the group number. If something is missing, ask the user instead of inventing it.
- Searching by topic, by group or by partial name, and updating or deleting documents,
  are not possible yet: if the user asks for them, say so clearly.
- If the request has nothing to do with the wiki documents, answer briefly yourself
  without calling the agents.

Answer the user in their language, in a short and clear way, based only on what the agents
reported: never claim a document was found or created unless an agent confirmed it."""

# Ogni sub agente riceve un solo parametro: il compito da svolgere, scritto per esteso
TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "task": {
            "type": "string",
            "description": "Complete, self-contained instruction for the agent: it cannot see the user conversation",
        },
    },
    "required": ["task"],
}

SUBAGENTS = {
    "ask_researcher": {
        "description": "Ask the researcher agent to find a wiki document by its exact file name. It can only read documents.",
        "input_schema": TASK_SCHEMA,
        "handler": researcher.run,
    },
    "ask_archivist": {
        "description": "Ask the archivist agent to add a new document (file name, group number, optional summary). It can only create documents.",
        "input_schema": TASK_SCHEMA,
        "handler": wiki.run,
    },
}


async def run(message: str, history: list[dict] | None = None) -> str:
    """Riceve il messaggio dell'utente, delega ai sub agenti e restituisce la risposta finale.

    `history` sono i messaggi precedenti della chat ({"role", "content"}), così l'orchestrator
    ricorda il contesto (es. l'utente risponde "gruppo 4" a una sua domanda).
    """
    messages = [*(history or []), {"role": "user", "content": message}]
    return await run_agent(SYSTEM_PROMPT, [], messages, local_tools=SUBAGENTS)
