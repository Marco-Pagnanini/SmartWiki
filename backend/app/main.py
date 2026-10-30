from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, health
from app.core.config import settings
from app.mcp_server import mcp
from app.tools import doc as doc_tools  # noqa: F401  (registra i tool MCP dei documenti)

# App HTTP del server MCP; stateless: ogni richiesta è indipendente
mcp_app = mcp.streamable_http_app(streamable_http_path="/mcp", stateless_http=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Il server MCP ha bisogno del suo gestore di sessioni attivo finché gira l'app
    async with mcp.session_manager.run():
        yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# CORS serve solo quando il frontend gira con `npm run dev` fuori da Docker
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)

# Server MCP raggiungibile su http://localhost:8000/mcp. Montato su "/" e per
# ultimo: le route FastAPI sopra hanno la precedenza, così /mcp non viene
# rediretto a /mcp/ (molti client MCP non seguono il redirect)
app.mount("/", mcp_app)
