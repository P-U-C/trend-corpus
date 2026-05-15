# Operations

Local validation:

```sh
make validate
make test
```

CI runs the same commands on push and pull request.

Public operations rules:

- Do not commit generated private runtime artifacts unless they are explicitly public and schema-valid.
- Do not commit databases, logs, broker configuration, OAuth files, webhooks, or personal trade context.
- Keep theme object files small and reviewable.
- Prefer append-only corpus updates. Supersede stale claims rather than silently rewriting evidence history.
- If a secret is exposed, rotate it before any other cleanup.

