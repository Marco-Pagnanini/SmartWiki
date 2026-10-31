from typing import Annotated

from pydantic import Field
from sqlalchemy.exc import IntegrityError

from mcp.server.mcpserver.exceptions import ToolError

from app.core.doc import Doc
from app.db.session import SessionLocal
from app.mcp_server import mcp
from app.service.doc import create_doc, get_doc_by_name, get_all_docs


def _to_dict(doc: Doc) -> dict:
    """Convert a Doc entity into a JSON-serializable dict for the AI."""
    return {
        "id": str(doc.id),
        "name_of_file": doc.name_of_file,
        "group_number": doc.group_number,
        "summary": doc.summary,
    }


@mcp.tool()
def add_document(
    name_of_file: Annotated[
        str,
        Field(min_length=1, max_length=255, description="unique name of file")
    ],
    group_number: Annotated[
        int,
        Field(ge=1, description="number of the group that own the document")
    ],
    summary: Annotated[
        str | None,
        Field(max_length=2000, description="summary of the document")
    ] = None,
) -> dict:
    """Add a new document to the wiki. The file name must be unique."""
    with SessionLocal() as db:
        try:
            doc = create_doc(db, name_of_file=name_of_file, group_number=group_number, summary=summary)
        except IntegrityError:
            raise ToolError(f"A document named '{name_of_file}' already exists")
        return _to_dict(doc)


@mcp.tool()
def get_document_by_name(
    name_of_file: Annotated[
        str,
        Field(min_length=1, max_length=255, description="exact name of the file to search")
    ],
) -> dict:
    """Find a document of the wiki by its exact file name and return its id, group and summary."""
    with SessionLocal() as db:
        doc = get_doc_by_name(db, name_of_file=name_of_file)
        if doc is None:
            raise ToolError(f"No document named '{name_of_file}'")
        return _to_dict(doc)

@mcp.tool()
def get_all_documents() -> list[dict]:
    """Return a list of all documents in the wiki."""
    with SessionLocal() as db:
        docs = get_all_docs(db)
        return [_to_dict(doc) for doc in docs]
