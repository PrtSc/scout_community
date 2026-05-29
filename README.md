# scout_community

Community-built integrations for **Team Cymru's Pure Signal Scout API** across frontier AI tools — Claude, ChatGPT, Microsoft Copilot, Google Gemini, Cursor/Windsurf/Cline/Zed, and Python agent frameworks (LangChain, LlamaIndex, AutoGen, CrewAI).

> This is an unofficial community resource. It is **not affiliated with, endorsed by, or supported by Team Cymru**. "Pure Signal" and "Scout" are trademarks of their respective owners.

## Why this exists

If you have a Scout community account (300 queries/month) and a Scout API key, this repo gives you drop-in artifacts to wire Scout into whichever AI assistant you use:

- `scout-openapi.yaml` — a complete OpenAPI 3.1 spec for the five Scout endpoints. Paste it into ChatGPT Custom GPT Actions, Microsoft Copilot Studio custom connectors, or any OpenAPI-to-MCP bridge.
- `mcp-server-python/` — a working Python MCP server you can register with Claude Desktop, Cursor, Windsurf, Cline, Zed, or any other MCP client.
- `mcp-server-node/` — the same MCP server in Node.js.
- `claude-desktop-config.example.json` — ready-to-paste Claude Desktop config.
- `langchain_tools.py` — LangChain `@tool` wrappers for the Scout endpoints.
- `gemini_function_calling.py` — Gemini function-calling declarations and a handler.
- `.env.example` — shows the env var layout. **Never commit a real key.**

## The Scout endpoints these tools expose

| Endpoint | Purpose | Costs a query? |
|---|---|---|
| `GET /api/scout/usage` | Check remaining monthly quota | No |
| `GET /api/scout/ip/foundation?ips=...` | Fast triage for up to 10 IPs | No (free triage path) |
| `GET /api/scout/search?query=...` | Scout query-language search | **Yes** |
| `GET /api/scout/ip/{ip}/details` | Deep enrichment for one IP | **Yes** |
| `GET /scout/tags/export` | Tag taxonomy CSV | No |

Authentication: send header `Authorization: Token YOUR_SCOUT_API_KEY`.

## Reusable system prompt

Drop this into the system prompt of any tool you connect:

> You are a threat-intelligence assistant with access to Team Cymru's Pure Signal Scout API. Use the Scout tools to investigate IPs, domains, certificates, banners, and fingerprints. Conserve quota: prefer `/api/scout/ip/foundation` for quick triage of up to 10 IPs, call `/api/scout/usage` before and after heavy work, and only call `/api/scout/search` or `/api/scout/ip/{ip}/details` when richer context is required. Always specify `start_date` and `end_date` (YYYY-MM-DD, UTC) and narrow the window to 7 days or less unless explicitly asked. When constructing queries, use specific selectors first (IP, domain, certificate hashes) before broad ones (asn, cc, port). Cite the Scout response data in your answers.

## Per-platform setup

### Claude Desktop, Cursor, Windsurf, Cline, Zed (MCP)

1. `cd mcp-server-python && pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your Scout API key.
3. Register the server with your MCP client. For Claude Desktop, copy `claude-desktop-config.example.json` into `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\\Claude\\claude_desktop_config.json` (Windows), and update the absolute path.
4. Restart the client. Four tools appear: `scout_usage`, `scout_search`, `scout_ip_details`, `scout_foundation`.

### ChatGPT Custom GPT (Plus/Pro/Team)

1. **Explore GPTs → Create → Configure → Actions → Create new action**.
2. Paste the contents of `scout-openapi.yaml`.
3. Under **Authentication** choose **API Key**, **Auth Type: Custom**, **Header Name: `Authorization`**, **Value: `Token YOUR_KEY`**.
4. Paste the system prompt above into Instructions.
5. Save as **Only me**.

### Microsoft Copilot Studio

1. **Tools → Add a tool → New connector**.
2. Upload `scout-openapi.yaml`.
3. Set **Authentication** to **API Key**, header name `Authorization`. Store the key value in Azure Key Vault for team use.

### Google Gemini (developer API)

Use `gemini_function_calling.py` as the reference handler. It declares the four Scout tools and forwards calls to the REST API.

### LangChain / LlamaIndex / AutoGen / CrewAI

Use `langchain_tools.py`. The same pattern translates one-for-one to LlamaIndex `FunctionTool`, AutoGen `register_function`, and CrewAI `@tool`.

## Quota-saving patterns

- **Triage first.** Always call `scout_foundation` before `scout_ip_details`. Foundation accepts up to 10 IPs at once and is the cheapest path to tags, ASN, and country.
- **Scoped window.** Pass `start_date` and `end_date` no wider than 7 days unless explicitly asked.
- **Specific selector first.** Lead Scout queries with selective fields (`pdns.domain`, `ip`, `x509.sha256`) before broad ones (`asn`, `cc`, `comms.port`).
- **No implicit refresh.** Cache responses; never re-run a details lookup just to "refresh".
- **Balance check.** Make `scout_usage` the first tool the agent calls in any session.

## Security

- Keep your Scout API key in a secret manager (1Password, Vault, Azure Key Vault, AWS Secrets Manager) or a local `.env` file that is **never committed**.
- Set Custom GPTs and Actions to **Only me** unless you have a rotation plan.
- For teams, run a single MCP/proxy server that holds the key and authenticates teammates separately.

## Need more queries?

Email `support@cymru.com` to expand your quota. Full Scout documentation: <https://scout.cymru.com/docs/scout>.

## License

MIT. See `LICENSE`.
