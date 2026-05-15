# trend-corpus

`trend-corpus` is a public template for building sector trend corpora that agents can maintain, validate, and hand off to private runtimes through file boundaries.

The repo contains shared taxonomy, object schemas, a validator, and reference themes. `peptides` is the canonical runtime pattern and is intentionally stubbed until M2. `llm-convergence` is filled now as a method theme for ranking cross-model ticker convergence as an attention signal.

## Use

1. Copy `trends/_template` to `trends/<sector-slug>`.
2. Fill in `trend.yaml` and add source, claim, entity, event, thesis, decision-packet, and watchlist objects.
3. Keep trade-relevant outputs gated at `execution_state: human_review_required`.
4. Run `make validate` and `make test`.

See [docs/theme-authoring.md](docs/theme-authoring.md) for the object workflow and [docs/new-sector-research-workflow.md](docs/new-sector-research-workflow.md) for the Claude/Codex research pattern.

