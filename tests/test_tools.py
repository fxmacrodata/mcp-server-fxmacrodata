"""Basic tests for mcp-server-fxmacrodata tool registration."""

import json

from mcp_server_fxmacrodata.server import mcp


EXPECTED_TOOLS = {
    "ping",
    "data_catalogue",
    "release_calendar",
    "forex",
    "indicator_query",
    "market_sessions",
    "cot_data",
    "commodities",
}


def test_all_tools_registered():
    """Every expected tool must be registered on the MCP server."""
    registered = {t.name for t in mcp._tool_manager.list_tools()}
    assert EXPECTED_TOOLS == registered, (
        f"Missing: {EXPECTED_TOOLS - registered}, Extra: {registered - EXPECTED_TOOLS}"
    )


def test_tool_descriptions_non_empty():
    """Each tool must have a non-empty description."""
    for tool in mcp._tool_manager.list_tools():
        assert tool.description, f"Tool {tool.name!r} has no description"
