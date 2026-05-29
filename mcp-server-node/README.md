# Scout MCP server (Node.js)

Same four tools as the Python server, in Node 18+.

## Install

```bash
cd mcp-server-node
npm install
cp ../.env.example .env
```

## Run standalone

```bash
node server.js
```

## Register with Claude Desktop

Use the same config block in `claude-desktop-config.example.json` but
change `command` to `node` and the path to `mcp-server-node/server.js`.
