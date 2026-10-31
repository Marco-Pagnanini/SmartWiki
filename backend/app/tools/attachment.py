from typing import Annotated

from pydantic import Field
from mcp.server.mcpserver.exceptions import ToolError

from app.mcp_server import mcp
from app.service.attachment import get_attachment

@mcp.tool()
def read_attachment(
    attachment_id: Annotated[
        str,
        Field(min_length=1, description="id of the file the user uploaded in the chat"),
    ],
) -> dict:
    """Read the text of a file the user uploaded in the chat, given its attachment id."""
    attachment = get_attachment(attachment_id)
    if attachment is None:
        raise ToolError(f"No attachment with id '{attachment_id}'")
    return {"filename": attachment.filename, "text": attachment.text}
