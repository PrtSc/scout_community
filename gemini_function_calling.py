"""
Gemini function-calling declarations and handler for the Scout API.

Requires:  pip install google-generativeai requests python-dotenv
Env:       SCOUT_API_KEY (required), GOOGLE_API_KEY (required)
"""
from __future__ import annotations

import os
import sys
from typing import Any

import requests
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

SCOUT_BASE = os.environ.get("SCOUT_BASE_URL", "https://scout.cymru.com")
SCOUT_KEY = os.environ["SCOUT_API_KEY"]
SCOUT_HEADERS = {"Authorization": f"Token {SCOUT_KEY}", "Accept": "application/json"}

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    r = requests.get(f"{SCOUT_BASE}{path}", headers=SCOUT_HEADERS, params=params or {}, timeout=60)
    r.raise_for_status()
    return r.json() if "json" in r.headers.get("content-type", "") else r.text


TOOLS = [
    {
        "name": "scout_usage",
        "description": "Return remaining Scout monthly quota.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "scout_foundation",
        "description": "Triage up to 10 comma-separated IPs.",
        "parameters": {
            "type": "object",
            "properties": {"ips": {"type": "string"}},
            "required": ["ips"],
        },
    },
    {
        "name": "scout_search",
        "description": "Scout query-language search. Decrements quota.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "size": {"type": "integer"},
            },
            "required": ["query", "start_date", "end_date"],
        },
    },
    {
        "name": "scout_ip_details",
        "description": "Deep enrichment for a single IP. Decrements quota.",
        "parameters": {
            "type": "object",
            "properties": {
                "ip": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "sections": {"type": "string"},
            },
            "required": ["ip", "start_date", "end_date"],
        },
    },
]


def dispatch(name: str, args: dict[str, Any]) -> Any:
    if name == "scout_usage":
        return _get("/api/scout/usage")
    if name == "scout_foundation":
        return _get("/api/scout/ip/foundation", {"ips": args["ips"]})
    if name == "scout_search":
        return _get("/api/scout/search", args)
    if name == "scout_ip_details":
        ip = args.pop("ip")
        return _get(f"/api/scout/ip/{ip}/details", args)
    raise ValueError(f"Unknown tool: {name}")


def main(prompt: str) -> None:
    model = genai.GenerativeModel(model_name="gemini-1.5-pro", tools=TOOLS)
    chat = model.start_chat()
    response = chat.send_message(prompt)
    for part in response.parts:
        fn = getattr(part, "function_call", None)
        if fn:
            result = dispatch(fn.name, dict(fn.args))
            response = chat.send_message(
                genai.protos.Content(
                    parts=[genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fn.name, response={"result": result}
                        )
                    )]
                )
            )
    print(response.text)


if __name__ == "__main__":
    main(" ".join(sys.argv[1:]) or "How many Scout queries do I have left?")
