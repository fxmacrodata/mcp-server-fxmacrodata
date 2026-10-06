# mcp-server-fxmacrodata

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for the [FXMacroData API](https://fxmacrodata.com/?utm_source=github&utm_medium=referral&utm_campaign=mcp-server-fxmacrodata&utm_content=readme): macroeconomic indicators, release calendars, COT positioning, commodities, and FX rates for AI agents.

Covers 22 currencies: AUD, BRL, CAD, CHF, CNH, CNY, DKK, EUR, GBP, HUF, ILS, JPY, KRW, MYR, NGN, NOK, NZD, PEN, SEK, THB, TWD, USD.

## Quick start

No install needed. Run with [`uvx`](https://docs.astral.sh/uv/guides/tools/):

```bash
uvx mcp-server-fxmacrodata
```

Evaluate the MCP server without an API key: USD announcements for the most
recent 90 days (each release readable 15 minutes after publication), the USD
release calendar, USD COT positioning, the data catalogue for every currency,
and market sessions. Connect an FXMacroData subscription for every currency,
real-time releases, full available history, FX rates and commodities:

```bash
FXMACRODATA_API_KEY=your_key uvx mcp-server-fxmacrodata
```

[Subscribe to FXMacroData](https://fxmacrodata.com/subscribe?utm_source=github&utm_medium=referral&utm_campaign=mcp-server-fxmacrodata&utm_content=subscribe), then connect the server using your own account's API key.

For a provider-agnostic install guide that works across multiple AI clients, see [llms-install.md](llms-install.md).

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

> **Tip:** If your MCP client supports remote HTTP servers, you can connect directly to `https://fxmacrodata.com/mcp` instead, with no local install. Append `?api_key=your_key` for non-USD data.

## Available tools

| Tool | Description |
|------|-------------|
| `ping` | Verify FXMacroData API connectivity |
| `data_catalogue` | List available indicators for a currency (keyless for every currency) |
| `release_calendar` | Upcoming macro release dates |
| `forex` | FX spot rates for any pair of supported currencies, with optional technical indicators |
| `indicator_query` | Macro indicator time series (announcements) |
| `market_sessions` | FX session timetable (Sydney, Tokyo, London, New York) |
| `cot_data` | CFTC Commitment of Traders positioning (AUD, CAD, CHF, EUR, GBP, JPY, NZD, USD) |
| `commodities` | Commodity prices (gold, silver, platinum) |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FXMACRODATA_API_KEY` | *(none)* | API key, sent as the `X-API-Key` header |
| `FXMACRODATA_BASE_URL` | `https://api.fxmacrodata.com` | Override API base URL (must be https, except localhost) |

## Install with pip

```bash
pip install mcp-server-fxmacrodata
```

Then run:

```bash
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

## License

MIT. See [LICENSE](LICENSE).
