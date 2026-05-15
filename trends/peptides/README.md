# Peptides

This is the canonical reference theme for trend-corpus. It mirrors the design of
an existing private peptide-corpus runtime that has been operating in production:
sources -> claims -> decision packets, with append-only supersedence and
category-driven half-lives.

## Why peptides is the template

The peptides runtime predates the public template and is the proof that the
pattern works. Anything you see here -- the source taxonomy, claim categories,
half-life defaults, prompt structures -- has been shaped by months of running
the loop on a live decision pipeline. New themes spun up under
`docs/new-sector-research-workflow.md` should follow the same shape unless they
have a specific reason to deviate.

## Architecture (mirrors the live runtime)

Pipeline:

```
sources --(ingest)--> raw_text --(extract via Claude Sonnet)--> claims
                                                                  |
                                                                  v
                                                packet.py (Claude Opus, on demand)
                                                                  |
                                                                  v
                                                          decision packet
```

Storage choices (proven in production, recommended for new sector spinups):

- SQLite + WAL. Single-writer is fine until you exceed thousands of claims.
- Append-only claims. Never update a claim; supersede it. A `superseded_by`
  pointer is the link.
- Half-life per claim category. Regulatory = 90 days, pricing = 30 days,
  corporate = 60, manufacturing = 180, market = 365, clinical = 3650. A
  `fresh_claims` view filters non-superseded claims still within half-life.
- Model tiering. Sonnet for extraction at scale, Opus for synthesis on demand.
- OAuth via Claude Code CLI, not API key. Subscription-covered. Credentials
  live in the runtime user's `~/.claude/`.

## What is in this directory

- `trend.yaml` -- theme manifest
- `sources/` -- one source object per upstream URL the ingest pipeline reads
- `claims/` -- example claims demonstrating the taxonomy. These are NOT pulled
  from the live database; they are illustrative.
- `entities/` -- example entities (companies and regulators) using the
  entity-slug convention
- `events/` -- example timestamped event
- `theses/` -- example thesis
- `decision-packets/` -- example decision packet with `execution_state:
  human_review_required`
- `watchlists/` -- example watchlist
- `docs/prompts.md` -- the live extraction / packet / supersedence prompts,
  verbatim (with ASCII-only conversion). These are the methodology and are the
  most directly reusable artifacts when spinning up a new sector.

## What is NOT in this directory

- No live claim history. The runtime's `db.sqlite` stays private.
- No generated packets. The actual decision packets reference live positions
  and stay private.
- No credentials, no API keys, no operator-specific endpoints.

## Reusing this for a new sector

See `docs/new-sector-research-workflow.md` at the repo root for the agent-spinup
pattern. Short version: copy `trends/_template/` into `trends/<your-sector>/`,
swap the sources, adapt the entity-slug conventions, keep the claim taxonomy
and half-lives unless you have a domain-specific reason to change them,
paraphrase `docs/prompts.md` for the new sector's vocabulary, run `make
validate`.
