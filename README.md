# mcp-server-fxmacrodata

Give your AI assistant real-time access to macroeconomic data across **18 currencies**.

Ask Claude, Copilot, Cursor, or any MCP-compatible agent questions like *"What did the RBA do with rates?"*, *"When is the next Fed decision?"*, or *"Show me EUR COT positioning"* — and get answers sourced directly from official central bank releases, not scraped headlines.

[![PyPI](https://img.shields.io/pypi/v/mcp-server-fxmacrodata)](https://pypi.org/project/mcp-server-fxmacrodata/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This is the official [Model Context Protocol](https://modelcontextprotocol.io) server for the [FXMacroData API](https://fxmacrodata.com) — the same data that powers the [FXMacroData dashboard](https://fxmacrodata.com/dashboard/market-summary), now available as typed tools for AI agents.

## What your agent gets access to

| Tool | What it does | Example question |
|------|-------------|-----------------|
| `indicator_query` | Macro indicator time series — policy rates, inflation, GDP, unemployment, trade balance, and dozens more | *"What is the latest AUD CPI reading?"* |
| `data_catalogue` | Browse all available indicators and currencies | *"What indicators are available for NZD?"* |
| `release_calendar` | Upcoming macro release dates with expected values | *"What USD data is coming out this week?"* |
| `forex` | FX spot rates with optional technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR) | *"Where is EUR/USD trading?"* |
| `cot_data` | CFTC Commitment of Traders positioning | *"Are specs net long or short GBP?"* |
| `commodities` | Gold, silver, and platinum prices | *"What is gold trading at?"* |
| `market_sessions` | Live FX session status (Sydney, Tokyo, London, New York) | *"Which FX sessions are open right now?"* |
| `ping` | Health check | *"Is the FXMacroData API up?"* |

**Currencies:** USD, EUR, GBP, JPY, AUD, CAD, CHF, NZD, HKD, SGD, NOK, PLN, SEK, DKK, BRL, CNY, KRW, MXN

**USD data is completely free** — no API key required. Non-USD data requires a key from [fxmacrodata.com/subscribe](https://fxmacrodata.com/subscribe).

## Quick start

No install needed — run directly with [`uvx`](https://docs.astral.sh/uv/guides/tools/):

```bash
uvx mcp-server-fxmacrodata
```

Or with an API key for all currencies:

```bash
FXMACRODATA_API_KEY=your_key uvx mcp-server-fxmacrodata
```

## Configure your MCP client

### Claude Desktop

Add to `claude_desktop_config.json`:

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

### Cursor

Add to `.cursor/mcp.json`:

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

### VS Code / GitHub Copilot

Add to `.vscode/mcp.json`:

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

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

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

### OpenClaw

Add to `~/.openclaw/openclaw.json`:

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

See the full [OpenClaw integration guide](https://fxmacrodata.com/articles/how-to-integrate-fxmacrodata-with-openclaw) for automated briefings and real-world workflow examples.

### Remote HTTP (no local install)

If your MCP client supports remote Streamable HTTP servers (Claude AI web, OpenClaw, etc.), skip the local install entirely:

```
https://fxmacrodata.com/mcp
```

For non-USD data, append your key: `https://fxmacrodata.com/mcp?api_key=your_key`

## What you can build

- **Pre-session macro scans** — "Summarize overnight prints for USD, EUR, GBP, and JPY before the London open"
- **Rate differential monitoring** — "What is the policy rate spread between the Fed and the ECB?"
- **Calendar-aware trade planning** — "Is there any high-impact data this week? I'm thinking about going long EUR/USD"
- **COT sentiment checks** — "Are speculators net long or short the yen?"
- **Automated morning briefings** — schedule your agent to deliver a macro summary every weekday before you start trading

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FXMACRODATA_API_KEY` | *(none)* | API key for non-USD currencies and commodities |
| `FXMACRODATA_BASE_URL` | `https://fxmacrodata.com/api` | Override API base URL |

## Install with pip

```bash
pip install mcp-server-fxmacrodata
mcp-server-fxmacrodata
```

## Development

```bash
git clone https://github.com/fxmacrodata/mcp-server-fxmacrodata
cd mcp-server-fxmacrodata
pip install -e ".[dev]"
pytest
```

## Debugging

Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector):

```bash
npx @modelcontextprotocol/inspector uvx mcp-server-fxmacrodata
```

## Learn more

- [MCP Server documentation](https://fxmacrodata.com/documentation/mcp-server) — full setup guide and tool reference
- [API documentation](https://fxmacrodata.com/documentation) — endpoint specs, quickstart, and changelog
- [OpenClaw integration guide](https://fxmacrodata.com/articles/how-to-integrate-fxmacrodata-with-openclaw) — connect to WhatsApp, Telegram, or Discord
- [How to use all API endpoints](https://fxmacrodata.com/articles/how-to-use-all-fxmacrodata-api-endpoints) — full endpoint tour
- [FXMacroData dashboard](https://fxmacrodata.com/dashboard/market-summary) — see the data in action
- [Python client library](https://pypi.org/project/fxmacrodata/) — `pip install fxmacrodata` for direct REST access

## License

MIT — see [LICENSE](LICENSE).
