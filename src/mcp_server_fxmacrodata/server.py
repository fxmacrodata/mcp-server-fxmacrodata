"""FXMacroData MCP Server — stdio transport for AI agent clients.

Exposes the full FXMacroData API surface as typed MCP tools that any
MCP-compatible client (Claude Desktop, Cursor, Windsurf, OpenClaw, etc.)
can discover and invoke.

Usage:
    uvx mcp-server-fxmacrodata                     # USD data (free)
    FXMACRODATA_API_KEY=key uvx mcp-server-fxmacrodata   # all currencies
"""

from __future__ import annotations

import json
import os

import httpx
from fxmacrodata import Client, FXMacroDataError
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_KEY = os.environ.get("FXMACRODATA_API_KEY", "")
BASE_URL = os.environ.get("FXMACRODATA_BASE_URL", "https://fxmacrodata.com/api")

_client = Client(api_key=API_KEY or None)

# Override base URL if the user changed it (e.g., for dev server).
if BASE_URL != "https://fxmacrodata.com/api":
    _client.BASE_URL = BASE_URL

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="FXMacroData",
    instructions=(
        "FXMacroData provides macroeconomic indicator data, release calendars, "
        "COT positioning, commodities, forex rates, and FX market session info. "
        "USD data is free. Non-USD data requires an API key."
    ),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _api_url(path: str) -> str:
    """Build a full API URL from a relative path."""
    return f"{BASE_URL}{path}"


def _auth_headers() -> dict[str, str]:
    """Return auth headers if an API key is configured."""
    if API_KEY:
        return {"X-API-Key": API_KEY}
    return {}


def _handle_error(tool_name: str, exc: Exception) -> str:
    """Format a tool error as a user-friendly JSON string."""
    msg = str(exc)
    if "API key required" in msg or "401" in msg:
        return json.dumps({
            "error": f"{tool_name} requires an API key for this request.",
            "help": "Set the FXMACRODATA_API_KEY environment variable. "
                    "Get your key at https://fxmacrodata.com/api-management",
        })
    return json.dumps({"error": msg})


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(
    name="ping",
    description="Verify that the FXMacroData API is reachable.",
)
def ping() -> str:
    """Health check."""
    resp = httpx.get(_api_url("/v1/ping"), headers=_auth_headers(), timeout=10)
    resp.raise_for_status()
    return json.dumps(resp.json())


@mcp.tool(
    name="data_catalogue",
    description=(
        "List available macroeconomic indicators for a currency. "
        "Supported currencies include: AUD, BRL, CAD, CHF, CNY, DKK, EUR, "
        "GBP, JPY, NZD, PLN, SEK, SGD, USD."
    ),
)
def data_catalogue(currency: str) -> str:
    """Return the indicator catalogue for a currency."""
    try:
        result = _client.get_data_catalogue(currency)
        return json.dumps(result)
    except FXMacroDataError as exc:
        return _handle_error("data_catalogue", exc)


@mcp.tool(
    name="release_calendar",
    description=(
        "Get upcoming macroeconomic release dates for a currency, with optional "
        "indicator filter."
    ),
)
def release_calendar(currency: str, indicator: str | None = None) -> str:
    """Return the release calendar for a currency."""
    try:
        result = _client.get_calendar(currency, indicator=indicator)
        return json.dumps(result)
    except FXMacroDataError as exc:
        return _handle_error("release_calendar", exc)


@mcp.tool(
    name="forex",
    description=(
        "Get FX spot rates for a currency pair with optional technical indicators. "
        "The indicators parameter accepts a comma-separated list of technical "
        "indicator slugs (e.g. 'sma_20,ema_50,rsi_14,bbands_20,atr_14,macd')."
    ),
)
def forex(
    base: str,
    quote: str,
    start_date: str | None = None,
    end_date: str | None = None,
    indicators: str | None = None,
) -> str:
    """Return FX spot rates and optional technical indicators."""
    try:
        result = _client.get_fx_price(
            base, quote,
            start_date=start_date,
            end_date=end_date,
            indicators=indicators,
        )
        return json.dumps(result)
    except FXMacroDataError as exc:
        return _handle_error("forex", exc)


@mcp.tool(
    name="indicator_query",
    description=(
        "Get macroeconomic indicator time series for a currency. "
        "Returns announcement dates, values, and prior readings. "
        "Use data_catalogue to discover valid currency + indicator slugs."
    ),
)
def indicator_query(
    currency: str,
    indicator: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Return an indicator announcement time series."""
    try:
        # Match the hosted MCP behaviour: COMM routes to commodities
        if currency.upper() == "COMM":
            result = _client.get_commodities(
                indicator, start_date=start_date, end_date=end_date,
            )
        else:
            result = _client.get_indicator(
                currency, indicator,
                start_date=start_date, end_date=end_date,
            )
        return json.dumps(result)
    except FXMacroDataError as exc:
        return _handle_error("indicator_query", exc)


@mcp.tool(
    name="market_sessions",
    description=(
        "Get the current FX market-session timetable and overlap windows, "
        "or request a snapshot for a specific UTC timestamp. "
        "Covers Sydney, Tokyo, London, and New York sessions."
    ),
)
def market_sessions(at: str | None = None) -> str:
    """Return FX market session status."""
    params: dict[str, str] = {}
    if at:
        params["at"] = at
    resp = httpx.get(
        _api_url("/v1/market_sessions"),
        params=params,
        headers=_auth_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    return json.dumps(resp.json())


@mcp.tool(
    name="cot_data",
    description=(
        "Get CFTC Commitment of Traders (COT) weekly positioning data "
        "for a currency's FX futures contract. "
        "Supported: AUD, CAD, CHF, EUR, GBP, JPY, NZD, USD."
    ),
)
def cot_data(
    currency: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Return COT positioning data for a currency."""
    try:
        result = _client.get_cot(
            currency, start_date=start_date, end_date=end_date,
        )
        return json.dumps(result)
    except FXMacroDataError as exc:
        return _handle_error("cot_data", exc)


@mcp.tool(
    name="commodities",
    description=(
        "Get commodity price time series. "
        "Supported indicators: gold, silver, platinum."
    ),
)
def commodities(
    indicator: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Return commodity price data."""
    try:
        result = _client.get_commodities(
            indicator, start_date=start_date, end_date=end_date,
        )
        return json.dumps(result)
    except FXMacroDataError as exc:
        return _handle_error("commodities", exc)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Run the MCP server on stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
