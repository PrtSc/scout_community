"""
Scout MCP server (Python).

Exposes four tools to any MCP client (Claude Desktop, Cursor, Windsurf,
Cline, Zed, etc.):
    - scout_usage
    - scout_foundation
    - scout_search
    - scout_ip_details

Requires:  pip install mcp httpx python-dotenv
Env:       SCOUT_API_KEY (required)
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

BASE_URL = os.environ.get("SCOUT_BASE_URL", "https://scout.cymru.com")
API_KEY = os.environ.get("SCOUT_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "SCOUT_API_KEY is not set. Add it to your environment or .env file."
    )

HEADERS = {
    "Authorization": f"Token {API_KEY}",
    "Accept": "application/json",
}

mcp = FastMCP("scout")


def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    with httpx.Client(timeout=60.0) as client:
        r = client.get(f"{BASE_URL}{path}", headers=HEADERS, params=params or {})
        r.raise_for_status()
        ctype = r.headers.get("content-type", "")
        return r.json() if "json" in ctype else r.text


@mcp.tool()
def scout_usage() -> Any:
    """Return current Scout API usage and remaining monthly quota."""
    return _get("/api/scout/usage")


@mcp.tool()
def scout_foundation(ips: str) -> Any:
    """Fast triage for up to 10 comma-separated IPs. Does not decrement quota.

    Args:
        ips: Comma-separated list of up to 10 IPs, e.g. "8.8.8.8,1.1.1.1".
    """
    return _get("/api/scout/ip/foundation", {"ips": ips})


@mcp.tool()
def scout_search(
    query: str,
    start_date: str | None = None,
    end_date: str | None = None,
    days: int | None = None,
    size: int | None = None,
) -> Any:
    """Run a Scout query-language search. Decrements quota.

    Lead with specific selectors (pdns.domain, ip, x509.sha256) before
    broad ones (asn, cc, comms.port).

    Args:
        query: Scout query, e.g. 'pdns.domain="*ngrok.io"'.
        start_date: UTC YYYY-MM-DD.
        end_date: UTC YYYY-MM-DD.
        days: Relative offset from now; overrides start_date/end_date.
        size: Page size (1..1000).
    """
    params: dict[str, Any] = {"query": query}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if days is not None:
        params["days"] = days
    if size is not None:
        params["size"] = size
    return _get("/api/scout/search", params)


@mcp.tool()
def scout_ip_details(
    ip: str,
    start_date: str | None = None,
    end_date: str | None = None,
    sections: str = "summary,comms,open_ports,pdns,x509,fingerprints,whois",
) -> Any:
    """Deep enrichment for a single IP. Decrements quota.

    Args:
        ip: IPv4 or IPv6 address.
        start_date: UTC YYYY-MM-DD.
        end_date: UTC YYYY-MM-DD.
        sections: Comma-separated sections from
            summary, proto_by_ip, comms, comms:client_server,
            open_ports, pdns, x509, fingerprints, whois.
    """
    params: dict[str, Any] = {"sections": sections}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    return _get(f"/api/scout/ip/{ip}/details", params)


if __name__ == "__main__":
    mcp.run()
