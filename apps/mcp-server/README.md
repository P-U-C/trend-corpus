# MCP Server Placeholder

The Model Context Protocol lets AI clients connect to external tools and resources through a typed server interface. This placeholder sketches a future MCP server for the metalayer.

Reference: https://modelcontextprotocol.io/

Future tools:

- `list_themes`: list registered public themes.
- `get_theme`: return one theme summary and object counts.
- `query_decision_packet`: route a question to a decision-packet-shaped review response.
- `list_watchlists`: list current watchlist summaries.

This placeholder does not implement live MCP tools. It exits cleanly so packaging and deployment shape can be reviewed without adding dependencies.

## Run

```sh
python3 server.py
```

