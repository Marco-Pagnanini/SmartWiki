from app.agents import researcher, wiki
from app.agents.runner import run_agent
from app.service.attachment import get_attachment

SYSTEM_PROMPT = """You are the assistant of SmartWiki, a company wiki of documents.
You talk with the user and coordinate two agents, available as tools:
- ask_researcher: finds a document by its exact file name. It can only read.
- ask_archivist: adds a new document (unique file name, group number >= 1, optional summary).
  It can also read a file the user attached and write the summary itself. It can only create.
You cannot read or change the wiki yourself: everything about documents goes through these agents.

How to work:
- Decide which agent the request needs. A request can need both, one after the other
  (for example: check whether a document exists, then add it).
- The agents cannot see this conversation. Every task you send must be complete and
  self-contained: always repeat the exact file name, group number and summary to use,
  never write things like "add it" or "the same document".
- Before asking the archivist to add a document, make sure the user gave the file name (or
  attached a file) and the group number. If something is missing, ask the user instead of
  inventing it.
- A message can end with "[Attached file: <name> (attachment id: <id>)]": the user uploaded
  that file. To add it, send the archivist the attachment id and the group number; the
  archivist reads the file and writes the summary, so never ask the user for a summary and
  never copy the file content into the task.
- Searching by topic, by group or by partial name, and updating or deleting documents,
  are not possible yet: if the user asks for them, say so clearly.
- If the request has nothing to do with the wiki documents, answer briefly yourself
  without calling the agents.

Answer the user in their language, in a short and clear way, based only on what the agents
reported: never claim a document was found or created unless an agent confirmed it."""

# Every sub agent takes a single parameter: the task to perform, written out in full
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
        "description": "Ask the archivist agent to add a new document (file name, group number, optional summary). Given an attachment id, it reads the uploaded file and writes the summary itself. It can only create documents.",
        "input_schema": TASK_SCHEMA,
        "handler": wiki.run,
    },
}


async def run(message: str, history: list[dict] | None = None, attachment_id: str | None = None) -> str:
    """Take the user's message, delegate to the sub agents and return the final answer.

    `history` holds the previous chat messages ({"role", "content", "attachment_id"}), so the
    orchestrator remembers the context (e.g. the user answers "group 4" to one of its questions).
    `attachment_id` is the id of a file uploaded with this message, if any.
    """
    if attachment_id is not None:
        if get_attachment(attachment_id) is None:
            raise ValueError(f"Attachment '{attachment_id}' not found: upload the file again")
        message = _with_attachment_note(message, attachment_id)

    messages = [_to_model_message(m) for m in history or []]
    messages.append({"role": "user", "content": message})
    return await run_agent(SYSTEM_PROMPT, [], messages, local_tools=SUBAGENTS)


def _to_model_message(item: dict) -> dict:
    """Turn a chat history item into a Claude API message (which has no attachment_id field)."""
    content = item["content"]
    if item.get("attachment_id"):
        content = _with_attachment_note(content, item["attachment_id"])
    return {"role": item["role"], "content": content}


def _with_attachment_note(text: str, attachment_id: str) -> str:
    """Append the attachment note the model reads: the file name and its id, never the text.

    The archivist reads the content itself with the read_attachment tool.
    """
    attachment = get_attachment(attachment_id)
    if attachment is None:
        # Uploads live in memory: after a restart the file of an old message is gone
        return f"{text}\n\n[Attached file no longer available: ask the user to upload it again]"
    return f"{text}\n\n[Attached file: {attachment.filename} (attachment id: {attachment_id})]"
