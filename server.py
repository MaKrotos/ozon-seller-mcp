"""
Entry point for Ozon Seller MCP Server.
Connects the client, utils and tools.
"""
import asyncio
from mcp.server.fastmcp import FastMCP
from .client import OzonClient
from .tools.products import register_products_tools
from .tools.orders import register_orders_tools
from .tools.analytics import register_analytics_tools
from .tools.communication import register_communication_tools

# Initialize MCP server
mcp = FastMCP("ozon-seller")

# Initialize Ozon API Client
ozon = OzonClient()

async def initialize_server():
    """Register all tool modules."""
    await register_products_tools(mcp, ozon)
    await register_orders_tools(mcp, ozon)
    await register_analytics_tools(mcp, ozon)
    await register_communication_tools(mcp, ozon)

async def _run():
    await initialize_server()
    await mcp.run_stdio_async()

def main():
    asyncio.run(_run())

if __name__ == "__main__":
    main()
