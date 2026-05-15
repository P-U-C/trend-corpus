#!/usr/bin/env python3
"""Stdlib placeholder API for the trend-corpus metalayer."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


HOST = "127.0.0.1"
PORT = 8080


THEMES = [
    {"id": "peptides", "title": "Peptides", "status": "peak_hype"},
    {"id": "llm-convergence", "title": "LLM Convergence", "status": "growing"},
]


WATCHLISTS = [
    {
        "id": "wl_high_convergence_tickers",
        "title": "High-convergence tickers across active themes",
        "execution_state": "human_review_required",
    }
]


def response_for(method: str, path: str) -> tuple[int, dict]:
    if method == "GET" and path == "/themes":
        return 200, {"themes": THEMES}

    if method == "GET" and path.startswith("/themes/"):
        theme_id = path.rsplit("/", 1)[-1]
        for theme in THEMES:
            if theme["id"] == theme_id:
                return 200, {"theme": theme}
        return 404, {"error": "theme not found"}

    if method == "GET" and path == "/convergence/latest":
        return 200, {
            "schema_version": 1,
            "generated_at": None,
            "generator": "metalayer-api-stub",
            "themes": [],
            "scores": [],
            "note": "placeholder only; real data is proxied from a private artifact",
        }

    if method == "GET" and path == "/watchlists":
        return 200, {"watchlists": WATCHLISTS}

    if method == "POST" and path == "/questions":
        return 202, {
            "decision_packet": {
                "id": "dp_placeholder",
                "question": "placeholder",
                "verdict": "human_review_queue",
                "execution_state": "human_review_required",
                "invalidation_conditions": [
                    "Real corpus routing has not been implemented."
                ],
            }
        }

    return 404, {"error": "route not found"}


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        status, payload = response_for("GET", path)
        self._send(status, payload)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length:
            self.rfile.read(length)
        status, payload = response_for("POST", path)
        self._send(status, payload)

    def log_message(self, fmt: str, *args) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"metalayer API stub listening on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()

