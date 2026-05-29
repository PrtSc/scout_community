/**
 * Scout MCP server (Node.js).
 *
 * Exposes four tools to any MCP client:
 *   - scout_usage
 *   - scout_foundation
 *   - scout_search
 *   - scout_ip_details
 *
 * Requires:  npm install @modelcontextprotocol/sdk dotenv
 * Env:       SCOUT_API_KEY (required)
 */
import 'dotenv/config';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const BASE_URL = process.env.SCOUT_BASE_URL || 'https://scout.cymru.com';
const API_KEY = process.env.SCOUT_API_KEY;
if (!API_KEY) {
  throw new Error('SCOUT_API_KEY is not set. Add it to your environment or .env file.');
}

const HEADERS = {
  Authorization: `Token ${API_KEY}`,
  Accept: 'application/json',
};

async function scoutGet(path, params = {}) {
  const url = new URL(`${BASE_URL}${path}`);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
  }
  const res = await fetch(url, { headers: HEADERS });
  if (!res.ok) {
    throw new Error(`Scout ${path} failed: ${res.status} ${await res.text()}`);
  }
  const ctype = res.headers.get('content-type') || '';
  return ctype.includes('json') ? res.json() : res.text();
}

const tools = [
  {
    name: 'scout_usage',
    description: 'Return current Scout API usage and remaining monthly quota.',
    inputSchema: { type: 'object', properties: {} },
  },
  {
    name: 'scout_foundation',
    description: 'Fast triage for up to 10 comma-separated IPs. Does not decrement quota.',
    inputSchema: {
      type: 'object',
      properties: { ips: { type: 'string', description: 'Comma-separated, up to 10 IPs.' } },
      required: ['ips'],
    },
  },
  {
    name: 'scout_search',
    description: 'Run a Scout query-language search. Decrements quota.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string' },
        start_date: { type: 'string', description: 'UTC YYYY-MM-DD' },
        end_date: { type: 'string', description: 'UTC YYYY-MM-DD' },
        days: { type: 'integer' },
        size: { type: 'integer' },
      },
      required: ['query'],
    },
  },
  {
    name: 'scout_ip_details',
    description: 'Deep enrichment for a single IP. Decrements quota.',
    inputSchema: {
      type: 'object',
      properties: {
        ip: { type: 'string' },
        start_date: { type: 'string' },
        end_date: { type: 'string' },
        sections: {
          type: 'string',
          default: 'summary,comms,open_ports,pdns,x509,fingerprints,whois',
        },
      },
      required: ['ip'],
    },
  },
];

const server = new Server({ name: 'scout', version: '1.0.0' }, { capabilities: { tools: {} } });

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools }));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args = {} } = req.params;
  let data;
  switch (name) {
    case 'scout_usage':
      data = await scoutGet('/api/scout/usage');
      break;
    case 'scout_foundation':
      data = await scoutGet('/api/scout/ip/foundation', { ips: args.ips });
      break;
    case 'scout_search':
      data = await scoutGet('/api/scout/search', args);
      break;
    case 'scout_ip_details': {
      const { ip, ...rest } = args;
      data = await scoutGet(`/api/scout/ip/${encodeURIComponent(ip)}/details`, rest);
      break;
    }
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
  return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
});

const transport = new StdioServerTransport();
await server.connect(transport);
