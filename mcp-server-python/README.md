# Scout MCP server (Python)

Wraps the Pure Signal Scout REST API as an MCP server. Works with Claude
Desktop, Cursor, Windsurf, Cline, Zed, and any other MCP client.

## Install

```bash
cd mcp-server-python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# edit .env and add your SCOUT_API_KEY
```

## Run standalone (smoke test)

```bash
python server.py
```

## Register with Claude Desktop

Open `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%\\Claude\\claude_desktop_config.json` (Windows) and
add the block from `claude-desktop-config.example.json` at the repo root.
Update the absolute path to `server.py` and your API key.

## Tools exposed

- `scout_usage()` — remaining monthly quota.
- `scout_foundation(ips)` — triage up to 10 IPs (free).
- `scout_search(query, start_date, end_date, days, size)` — query-language search.
- `scout_ip_details(ip, start_date, end_date, sections)` — deep enrichment.
