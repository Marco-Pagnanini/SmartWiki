from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import attachment, chat, health
from app.core.config import settings
from app.mcp_server import mcp
from app.tools import doc as doc_tools  # noqa: F401  (registers the document MCP tools)
from app.tools import attachment as attachment_tools  # noqa: F401  (registers the attachment MCP tools)

# HTTP app of the MCP server; stateless: every request is independent
mcp_app = mcp.streamable_http_app(streamable_http_path="/mcp", stateless_http=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # The MCP server needs its session manager running for as long as the app runs
    async with mcp.session_manager.run():
        yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# CORS is only needed when the frontend runs with `npm run dev` outside Docker
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(attachment.router)

# MCP server reachable at http://localhost:8000/mcp. Mounted on "/" and last:
# the FastAPI routes above take precedence, so /mcp is not redirected
# to /mcp/ (many MCP clients do not follow the redirect)
app.mount("/", mcp_app)
