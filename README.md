# mcp-server-fxmacrodata

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for the [FXMacroData API](https://fxmacrodata.com) — macroeconomic indicators, release calendars, COT positioning, commodities, and FX rates for AI agents.

## Quick start

No install needed — run with [`uvx`](https://docs.astral.sh/uv/guides/tools/):

```bash
uvx mcp-server-fxmacrodata
```

USD data works immediately with no API key. For all currencies, set your key:

```bash
FXMACRODATA_API_KEY=your_key uvx mcp-server-fxmacrodata
```

Get a free API key at [fxmacrodata.com/api-management](https://fxmacrodata.com/api-management).

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

> **Tip:** If your MCP client supports remote HTTP servers, you can connect directly to `https://fxmacrodata.com/mcp` instead — no local install needed. Append `?api_key=your_key` for non-USD data.

## Available tools

| Tool | Description |
|------|-------------|
| `ping` | Verify FXMacroData API connectivity |
| `data_catalogue` | List available indicators for a currency |
| `release_calendar` | Upcoming macro release dates |
| `forex` | FX spot rates with optional technical indicators |
| `indicator_query` | Macro indicator time series (announcements) |
| `market_sessions` | FX session timetable (Sydney, Tokyo, London, New York) |
| `cot_data` | CFTC Commitment of Traders positioning |
| `commodities` | Commodity prices (gold, silver, platinum) |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FXMACRODATA_API_KEY` | *(none)* | API key for non-USD data |
| `FXMACRODATA_BASE_URL` | `https://fxmacrodata.com/api` | Override API base URL |

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

MIT — see [LICENSE](LICENSE).
