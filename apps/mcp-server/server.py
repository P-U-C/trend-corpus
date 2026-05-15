#!/usr/bin/env python3
"""Placeholder MCP server entry point.

The real implementation will expose typed tools over MCP. This stub avoids
runtime dependencies while keeping the deployment shape visible.
"""

from __future__ import annotations

import json


TOOLS = [
    "list_themes",
    "get_theme",
    "query_decision_packet",
    "list_watchlists",
]


def main() -> int:
    payload = {
        "name": "trend-corpus-metalayer-mcp-stub",
        "status": "stub",
        "tools": TOOLS,
    }
    print("MCP server stub")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

