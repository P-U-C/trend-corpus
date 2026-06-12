# Install Runbook

This runbook brings up a fresh private host with the public `trend-corpus` repo, validator dependencies, and placeholder metalayer services.

The peptides runtime is the canonical reference pattern: local runtime state, SQLite WAL while scale is modest, append-only claims, and public-safe artifacts crossing a file boundary.

## 1. Prepare The Host

Install base packages:

```sh
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip make
```

Optional container runtime:

```sh
sudo apt-get install -y docker.io docker-compose-plugin
```

Confirm Python:

```sh
python3 --version
```

## 2. Clone Or Place The Public Repo

For development on this box, use:

```sh
cd ~
git clone <public-repo-url> trend-corpus
cd trend-corpus
```

If the repo already exists:

```sh
cd ~/trend-corpus
git status --short
```

Do not place private runtime databases, logs, credentials, or generated private packets inside this repo.

## 3. Install Validator Dependencies

Create a local virtual environment if desired:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pyyaml pytest
```

The validator is intentionally small. PyYAML and pytest are the only expected test-time dependencies.

## 4. Validate The Public Corpus

Run:

```sh
make validate
make test
```

Both commands must pass before wiring private runtimes to this checkout.

## 5. Configure Private Runtime Paths

The placeholder apps need no environment variables, but a real deployment should set:

```sh
export TREND_CORPUS_PATH="$HOME/trend-corpus"
export CONVERGENCE_ARTIFACT_PATH="$HOME/puc-trading/corpus/convergence-latest.json"
export PRIVATE_RUNTIME_STATE_URL="http://127.0.0.1:9000/state"
```

Keep these values in private deployment config, not in committed files.

## 6. Optional Compose Shape Check

The Makefile targets are documentation stubs:

```sh
make up
make down
```

To inspect the private deployment shape manually:

```sh
cd ops
docker compose config
```

The compose file is a placeholder. It describes the metalayer API, MCP server, a future Postgres service, and an optional reverse proxy.

## 7. Start Placeholder Apps Manually

Metalayer API:

```sh
cd ~/trend-corpus/apps/metalayer-api
python3 app.py
```

MCP server placeholder:

```sh
cd ~/trend-corpus/apps/mcp-server
python3 server.py
```

## 8. Operational Checks

Before considering the host ready:

- `make validate` passes.
- `make test` passes.
- Private runtime paths point outside the public repo.
- No runtime database or generated private packet lives under `~/trend-corpus`.
- Any trade-relevant packet remains gated at `human_review_required`.

## 9. Per-Theme Runtime Bring-Up Order

Whenever spinning up a new per-theme runtime user (e.g. `solidstate`,
`synbio`, `edgeai`), follow this order exactly. Skipping `init` is the
canonical failure mode -- the first `ingest` cron will crash with
`sqlite3.OperationalError: no such table: sources`.

```sh
# As the theme user, in the theme working dir, with TRT_CONFIG set:
python3 -m theme_runtime sync --from "$HOME/trend-corpus"   # writes sources.txt + prompts/
python3 -m theme_runtime init                               # creates db.sqlite schema
python3 -m theme_runtime health                             # verifies claude CLI auth
python3 -m theme_runtime ingest                             # smoke-test one ingest cycle
python3 -m theme_runtime notify alert "deploy-test ping"    # smoke-test Telegram path
```

Only after all five succeed should `/etc/cron.d/<user>-corpus` be
installed. The Telegram alert verifies bot routing (sector runtimes
post via the runtime bot, not the Codex / orchestrator bot).

## 10. Claude CLI Authentication (Per-User, Long-Lived)

Each runtime user invokes the `claude` CLI from cron for the LLM
extraction step. The CLI requires a valid auth token. Use
`claude setup-token` (not the OAuth `/login` flow) so the token is
long-lived and doesn't depend on a silent refresh loop.

Why: a refresh-token revocation in May 2026 silently invalidated all
14 sector runtime users' OAuth credentials. The CLI kept hitting the
API with the expired access token and returning 401s; ingest fetched
sources but extraction returned `claude CLI failed (exit 1)` for ~3
days before the operator noticed the digest pattern
(`claims: +0 new / sources: N errored`). `setup-token` issues a
long-lived API token that does not auto-expire, eliminating that
failure mode.

### One-time per user

As the runtime user, in any directory:

```sh
claude setup-token
```

The CLI prints a URL and a code. Open the URL in a browser logged in
to the operator's Claude.ai account, paste the code, and approve.
The CLI saves the token to `~/.claude/.credentials.json` and exits.

Verify:

```sh
echo hi | claude --print
```

A 401 means the token was not saved or is invalid; re-run
`claude setup-token`. A coherent reply means the user is ready.

### Bulk re-auth (city-worker-301)

The orchestration repo ships a helper that walks through all 14
sector users sequentially:

```sh
ssh city-worker-peptides
sudo bash /home/ubuntu/reauth-runtimes.sh
```

The script runs `claude setup-token` per user, verifies with a
`claude --print` smoke test, and prints a final summary of OK / FAIL
users. ~30-60 seconds per user once the operator has a browser tab
ready.

### Monitoring

A daily check should flag any sector whose 24h digest reports
`claims: +0 new` while `sources: N errored` for N > fetch-floor. That
pattern almost always means the LLM extractor is dead (auth or rate),
not that the sources are bad. The auth path should not be allowed to
fail silently for more than 24 hours again.

## 11. Peptides Reference

Use peptides as the reference runtime pattern:

- Sources are gathered from public upstream URLs.
- Claims are append-only and can be superseded.
- Category half-lives determine freshness.
- Decision packets cite supporting claims and define invalidation conditions.
- Public outputs stop at human review when trade relevance exists.

