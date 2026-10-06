"""FXMacroData MCP Server: stdio transport for AI agent clients.

Exposes the FXMacroData API surface as typed MCP tools that any
MCP-compatible client (Claude Desktop, Cursor, Windsurf, OpenClaw, etc.)
can discover and invoke.

Usage:
    uvx mcp-server-fxmacrodata                     # USD data (free)
    FXMACRODATA_API_KEY=key uvx mcp-server-fxmacrodata   # all currencies
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import quote, urlsplit

import httpx
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "https://api.fxmacrodata.com"

# The 22 currencies in the public FXMacroData catalogue
# (https://fxmacrodata.com/llms.txt, GET /v1/data_catalogue/{currency}).
SUPPORTED_CURRENCIES = (
    "AUD", "BRL", "CAD", "CHF", "CNH", "CNY", "DKK", "EUR", "GBP", "HUF", "ILS",
    "JPY", "KRW", "MYR", "NGN", "NOK", "NZD", "PEN", "SEK", "THB", "TWD", "USD",
)
_CURRENCY_LIST = ", ".join(SUPPORTED_CURRENCIES)

COT_CURRENCIES = ("AUD", "CAD", "CHF", "EUR", "GBP", "JPY", "NZD", "USD")

REQUEST_TIMEOUT = httpx.Timeout(30.0, connect=10.0)

API_KEY = os.environ.get("FXMACRODATA_API_KEY", "").strip()


def _resolve_base_url(raw: str | None) -> str:
    """Return the API base URL, refusing plain HTTP except for local hosts.

    The API key is sent on every request, so it must never go over an
    unencrypted connection to a remote host.
    """
    base = (raw or DEFAULT_BASE_URL).strip().rstrip("/")
    parts = urlsplit(base)
    local = parts.hostname in {"localhost", "127.0.0.1", "::1"}
    if parts.scheme == "https" or (parts.scheme == "http" and local):
        return base
    raise ValueError(
        "FXMACRODATA_BASE_URL must be an https:// URL "
        "(plain http is only accepted for localhost)."
    )


BASE_URL = _resolve_base_url(os.environ.get("FXMACRODATA_BASE_URL"))

# Redirects are never followed: a redirect would re-send the API key header
# to whatever host the Location points at.
_http = httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=False)

SUBSCRIBE_HELP = (
    "Set the FXMACRODATA_API_KEY environment variable. "
    "Get your key at https://fxmacrodata.com/api-management"
    "?utm_source=mcp&utm_medium=integration"
    "&utm_campaign=mcp-server-fxmacrodata&utm_content=error"
)

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="FXMacroData",
    instructions=(
        "FXMacroData provides macroeconomic indicator data, release calendars, "
        "COT positioning, commodities, forex rates, and FX market session info "
        f"for 22 currencies: {_CURRENCY_LIST}. "
        "Without an API key: USD announcements for the most recent 90 days "
        "(each release readable 15 minutes after publication), the USD release "
        "calendar, USD COT positioning, the data catalogue for every currency, "
        "and market sessions. An API key unlocks every currency, real-time "
        "releases, full history, forex rates and commodities."
    ),
)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

class FXMacroDataAPIError(Exception):
    """An API call failed. The message never contains the API key."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _redact(text: str) -> str:
    """Remove the configured API key from any text before it is returned."""
    if API_KEY and API_KEY in text:
        text = text.replace(API_KEY, "***")
    return text


def _auth_headers() -> dict[str, str]:
    """Return auth headers if an API key is configured."""
    if API_KEY:
        return {"X-API-Key": API_KEY}
    return {}


def _segment(value: str) -> str:
    """Normalise one URL path segment (currency, indicator, pair leg)."""
    return quote(value.strip().lower(), safe="")


def _error_message(body: Any) -> str | None:
    """Return the error text if a JSON body is an error payload."""
    if not isinstance(body, dict):
        return None
    for key in ("error", "detail", "message"):
        value = body.get(key)
        if isinstance(value, str) and value and "data" not in body:
            return value
    if body.get("error"):
        return json.dumps(body["error"])
    return None


def _request(path: str, params: dict[str, str] | None = None) -> Any:
    """GET an API path and return the decoded JSON body.

    Raises FXMacroDataAPIError for transport failures, redirects, non-200
    responses, non-JSON bodies and 200 responses that carry an error payload.
    """
    query = {k: v for k, v in (params or {}).items() if v is not None}
    try:
        resp = _http.get(f"{BASE_URL}{path}", params=query, headers=_auth_headers())
    except httpx.TimeoutException:
        raise FXMacroDataAPIError("Request to the FXMacroData API timed out.") from None
    except httpx.HTTPError as exc:
        raise FXMacroDataAPIError(
            _redact(f"Request to the FXMacroData API failed: {type(exc).__name__}")
        ) from None

    if resp.is_redirect:
        raise FXMacroDataAPIError(
            f"Unexpected redirect ({resp.status_code}) from the FXMacroData API; "
            "not followed.",
            resp.status_code,
        )

    try:
        body = resp.json()
    except ValueError:
        body = None

    if resp.status_code != 200:
        detail = _error_message(body) or resp.reason_phrase or "request failed"
        raise FXMacroDataAPIError(_redact(f"{resp.status_code}: {detail}"), resp.status_code)

    if body is None:
        raise FXMacroDataAPIError("The FXMacroData API returned a non-JSON response.", 200)

    error = _error_message(body)
    if error:
        raise FXMacroDataAPIError(_redact(error), 200)

    return body


def _handle_error(tool_name: str, exc: FXMacroDataAPIError) -> str:
    """Format a tool error as a user-friendly JSON string."""
    if exc.status_code in (401, 402, 403):
        return json.dumps({
            "error": f"{tool_name} requires an API key for this request.",
            "detail": _redact(str(exc)),
            "help": SUBSCRIBE_HELP,
        })
    return json.dumps({"error": _redact(str(exc))})


def _call(tool_name: str, path: str, params: dict[str, str] | None = None) -> str:
    try:
        return json.dumps(_request(path, params))
    except FXMacroDataAPIError as exc:
        return _handle_error(tool_name, exc)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(
    name="ping",
    description="Verify that the FXMacroData API is reachable.",
)
def ping() -> str:
    """Health check."""
    return _call("ping", "/v1/ping")


@mcp.tool(
    name="data_catalogue",
    description=(
        "List available macroeconomic indicators for a currency. Works without "
        f"an API key for every currency. Supported currencies: {_CURRENCY_LIST}."
    ),
)
def data_catalogue(currency: str) -> str:
    """Return the indicator catalogue for a currency."""
    return _call("data_catalogue", f"/v1/data_catalogue/{_segment(currency)}")


@mcp.tool(
    name="release_calendar",
    description=(
        "Get upcoming macroeconomic release dates for a currency, with optional "
        "indicator filter. USD works without an API key; other currencies need one. "
        f"Supported currencies: {_CURRENCY_LIST}."
    ),
)
def release_calendar(currency: str, indicator: str | None = None) -> str:
    """Return the release calendar for a currency."""
    return _call(
        "release_calendar",
        f"/v1/calendar/{_segment(currency)}",
        {"indicator": indicator},
    )


@mcp.tool(
    name="forex",
    description=(
        "Get FX spot rates for a currency pair with optional technical indicators. "
        "Both legs must be supported currencies. Requires an API key. "
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
    return _call(
        "forex",
        f"/v1/forex/{_segment(base)}/{_segment(quote)}",
        {"start_date": start_date, "end_date": end_date, "indicators": indicators},
    )


@mcp.tool(
    name="indicator_query",
    description=(
        "Get macroeconomic indicator time series for a currency. "
        "Returns announcement dates, values, and prior readings. "
        "Without an API key only USD is available (most recent 90 days, each "
        "release readable 15 minutes after publication). "
        f"Supported currencies: {_CURRENCY_LIST}. "
        "Use data_catalogue to discover valid indicator slugs."
    ),
)
def indicator_query(
    currency: str,
    indicator: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Return an indicator announcement time series."""
    params = {"start_date": start_date, "end_date": end_date}
    # Match the hosted MCP behaviour: COMM routes to commodities
    if currency.strip().upper() == "COMM":
        return _call("indicator_query", f"/v1/commodities/{_segment(indicator)}", params)
    return _call(
        "indicator_query",
        f"/v1/announcements/{_segment(currency)}/{_segment(indicator)}",
        params,
    )


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
    return _call("market_sessions", "/v1/market_sessions", {"at": at})


@mcp.tool(
    name="cot_data",
    description=(
        "Get CFTC Commitment of Traders (COT) weekly positioning data "
        "for a currency's FX futures contract. "
        f"Supported: {', '.join(COT_CURRENCIES)}. USD works without an API key."
    ),
)
def cot_data(
    currency: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Return COT positioning data for a currency."""
    return _call(
        "cot_data",
        f"/v1/cot/{_segment(currency)}",
        {"start_date": start_date, "end_date": end_date},
    )


@mcp.tool(
    name="commodities",
    description=(
        "Get commodity price time series. Requires an API key. "
        "Supported indicators: gold, silver, platinum."
    ),
)
def commodities(
    indicator: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Return commodity price data."""
    return _call(
        "commodities",
        f"/v1/commodities/{_segment(indicator)}",
        {"start_date": start_date, "end_date": end_date},
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Run the MCP server on stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
