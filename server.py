"""MCP entry point for Claude Desktop and other MCP clients.

The shopping logic lives in app/services/catalog.py so it can be reused by the
web API instead of having two separate implementations.
"""
from mcp.server.fastmcp import FastMCP

from app.services.catalog import search_catalog_markdown

mcp = FastMCP("E-Commerce Price Comparator")


@mcp.tool()
def search_and_scrape_products(query: str) -> str:
    """Search supported Indian fashion stores and return source markdown."""
    return search_catalog_markdown(query)


if __name__ == "__main__":
    mcp.run(transport="stdio")
