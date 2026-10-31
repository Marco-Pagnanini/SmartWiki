from mcp.server.mcpserver import MCPServer

from app.core.config import settings

# MCP server: tools registered with @mcp.tool() become functions an AI agent
# can call. It is mounted on FastAPI at /mcp (see main.py).
mcp = MCPServer(name=settings.APP_NAME)

# Files that define tools must be imported in main.py,
# otherwise their @mcp.tool() never runs and the tools do not exist.
