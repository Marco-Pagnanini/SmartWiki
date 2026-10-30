from mcp.server.mcpserver import MCPServer

from app.core.config import settings

# Server MCP: i tool registrati con @mcp.tool() diventano funzioni che un
# agente AI può chiamare. È montato su FastAPI all'indirizzo /mcp (vedi main.py).
mcp = MCPServer(name=settings.APP_NAME)

# I file che definiscono tool vanno importati in main.py,
# altrimenti i loro @mcp.tool() non vengono mai eseguiti e i tool non esistono.
