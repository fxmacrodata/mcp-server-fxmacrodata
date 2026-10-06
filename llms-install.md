# FXMacroData MCP - Universal Install Guide

This guide is written for AI agents and humans installing FXMacroData MCP across multiple clients, not only one marketplace or editor.

## 1. What this repo is

- Package: `mcp-server-fxmacrodata`
- Purpose: a local MCP server for the FXMacroData API
- Transport: stdio MCP
- Primary install path: `uvx mcp-server-fxmacrodata`

Covers 22 currencies: AUD, BRL, CAD, CHF, CNH, CNY, DKK, EUR, GBP, HUF, ILS, JPY, KRW, MYR, NGN, NOK, NZD, PEN, SEK, THB, TWD, USD.

USD announcements (most recent 90 days, 15 minutes after publication), the USD release calendar, USD COT and the data catalogue work without an API key. Other currencies, real-time releases, full history, FX rates and commodities require `FXMACRODATA_API_KEY`.

## 2. Quick start

Use the no-install path first:

```bash
uvx mcp-server-fxmacrodata
```

For full access:

```bash
FXMACRODATA_API_KEY=your_key uvx mcp-server-fxmacrodata
```

If your environment prefers pip:

```bash
pip install mcp-server-fxmacrodata
mcp-server-fxmacrodata
```

## 3. Client configuration

Use the snippet format your client expects.

### Claude Desktop / Cursor / OpenClaw-style `mcpServers`

```json
{
  "mcpServers": {
    "fxmacrodata": {
      "command": "uvx",
      "args": ["mcp-server-fxmacrodata"],
      "env": {
        "FXMACRODATA_API_KEY": "your_key"
      }
    }
  }
}
```

### VS Code / GitHub Copilot-style `servers`

```json
{
  "servers": {
    "fxmacrodata": {
      "command": "uvx",
      "args": ["mcp-server-fxmacrodata"],
      "env": {
        "FXMACRODATA_API_KEY": "your_key"
      }
    }
  }
}
```

## 4. Recommended verification flow

1. Start the server.
2. Confirm the client connects.
3. Call `tools/list`.
4. Run a public tool first, such as `ping` or `data_catalogue` with `USD`.
5. Run a non-USD call only after setting `FXMACRODATA_API_KEY`.

Suggested smoke tests:

```bash
uvx mcp-server-fxmacrodata
```

Then ask the client:

1. "List the available USD indicators."
2. "Show upcoming USD GDP releases."
3. "Get EUR inflation data for the last 12 months."

## 5. Supported tools

- `ping`
- `data_catalogue`
- `release_calendar`
- `forex`
- `indicator_query`
- `market_sessions`
- `cot_data`
- `commodities`

## 6. API key guidance

- Store the API key in the client environment, not in source control.
- The key is sent as the `X-API-Key` header on every request, so USD releases arrive in real time.
- USD paths work without a key, on a 15-minute delay.

## 7. Troubleshooting

1. The client says no tools are available:
- Re-check that the command is `uvx mcp-server-fxmacrodata`.
- Restart the client after changing the config.

2. Non-USD requests fail:
- Confirm `FXMACRODATA_API_KEY` is set.
- Try a fresh terminal session so the environment variable is loaded.

3. Python package install fails:
- Prefer `uvx` first.
- If using pip, ensure your Python environment is up to date.

4. The client expects a remote MCP server:
- This repo is the local stdio server package.
- If you need the hosted remote endpoint, use the FXMacroData MCP service at https://fxmacrodata.com/mcp.

## 8. Policy and support links

- Main website: https://fxmacrodata.com/?utm_source=github&utm_medium=referral&utm_campaign=mcp-server-fxmacrodata&utm_content=llms-install
- API management: https://fxmacrodata.com/api-management?utm_source=github&utm_medium=referral&utm_campaign=mcp-server-fxmacrodata&utm_content=llms-install
- Privacy policy: https://fxmacrodata.com/privacy?utm_source=github&utm_medium=referral&utm_campaign=mcp-server-fxmacrodata&utm_content=llms-install
- Terms: https://fxmacrodata.com/terms?utm_source=github&utm_medium=referral&utm_campaign=mcp-server-fxmacrodata&utm_content=llms-install
- Support: info@fxmacrodata.com

## 9. Copy for installers

If an autonomous installer agent needs a one-line summary, use this:

> Install FXMacroData MCP with `uvx mcp-server-fxmacrodata`, then set `FXMACRODATA_API_KEY` for non-USD access.
