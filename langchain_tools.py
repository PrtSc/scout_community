"""
LangChain @tool wrappers for the Pure Signal Scout API.

Requires:  pip install langchain requests python-dotenv
Env:       SCOUT_API_KEY (required)

Usage:
    from langchain_tools import SCOUT_TOOLS
    # Pass SCOUT_TOOLS to your agent (e.g. create_react_agent).
"""
from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

BASE = os.environ.get("SCOUT_BASE_URL", "https://scout.cymru.com")
API_KEY = os.environ.get("SCOUT_API_KEY")
if not API_KEY:
    raise RuntimeError("SCOUT_API_KEY is not set.")

HEADERS = {"Authorization": f"Token {API_KEY}", "Accept": "application/json"}


def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    r = requests.get(f"{BASE}{path}", headers=HEADERS, params=params or {}, timeout=60)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    return r.json() if "json" in ctype else r.text


@tool
def scout_usage() -> dict:
    """Return remaining Scout monthly quota. Does not decrement quota."""
    return _get("/api/scout/usage")


@tool
def scout_foundation(ips: str) -> dict:
    """Triage up to 10 comma-separated IPs. Does not decrement quota."""
    return _get("/api/scout/ip/foundation", {"ips": ips})


@tool
def scout_search(
    query: str,
    start_date: str,
    end_date: str,
    size: int = 50,
) -> dict:
    """Run a Scout query-language search. Decrements quota.

    Lead with specific selectors (pdns.domain, ip, x509.sha256) before
    broad ones. Dates are UTC YYYY-MM-DD; keep the window <= 7 days.
    """
    return _get(
        "/api/scout/search",
        {"query": query, "start_date": start_date, "end_date": end_date, "size": size},
    )


@tool
def scout_ip_details(
    ip: str,
    start_date: str,
    end_date: str,
    sections: str = "summary,comms,open_ports,pdns,x509,fingerprints,whois",
) -> dict:
    """Deep enrichment for a single IP. Decrements quota."""
    return _get(
        f"/api/scout/ip/{ip}/details",
        {"start_date": start_date, "end_date": end_date, "sections": sections},
    )


SCOUT_TOOLS = [scout_usage, scout_foundation, scout_search, scout_ip_details]
