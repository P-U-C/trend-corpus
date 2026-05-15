# Scanner Integration Runbook

This runbook describes how public trend themes connect to the private scanner runtime through a file boundary.

The scanner remains private. The public corpus defines schemas, themes, and method documentation.

## 1. Boundary

The boundary is a generated JSON artifact:

```text
~/puc-trading/corpus/convergence-latest.json
```

The artifact must match:

```text
schemas/convergence.schema.json
```

The scanner consumes the artifact. It does not import public corpus-populator code or hold public repo credentials.

## 2. M1 Contract

The convergence artifact includes:

- `schema_version`
- `generated_at`
- `generator`
- `themes`
- `scores`

Each score row must include:

- `ticker`
- `theme`
- `score`
- `tier`
- `status`

Additional provenance fields preserve auditability:

- `company_name`
- `theme_id`
- `models_mentioning`
- `total_mentions`
- `avg_rank`
- `direct_recommendation_count`
- `hedged_mention_count`

## 3. Theme Join Key

Theme names and IDs must stay stable.

The scanner groups and joins on theme values. If a public theme slug changes, update the private artifact generator and scanner configuration in the same deployment window.

Avoid renaming themes after launch.

## 4. Freshness Check

The scanner must reject stale artifacts.

The M1 freshness check applies:

- Read `generated_at`.
- Compare it with the configured maximum age.
- Fail loudly if the artifact is missing or stale.
- Do not silently scan an empty or old convergence list.

Freshness failures should produce an operator-visible error and no promoted packet.

## 5. Public Validation

Before generating private artifacts:

```sh
cd ~/trend-corpus
make validate
make test
```

Public validation catches:

- Schema failures.
- Broken references.
- Missing invalidation conditions.
- Forbidden public execution states.
- Secret-pattern hits.

## 6. Private Scanner Flow

The public Makefile includes placeholder targets:

```sh
make populate-convergence
make scan
```

The real scanner flow lives in the private runtime:

```sh
cd ~/puc-trading
make scan
```

If no Makefile exists in the private runtime, run the scanner command documented by that repo instead.

## 7. Daily Operation

A normal private schedule is:

1. Refresh public corpus checkout.
2. Run public validation.
3. Run the private convergence populator.
4. Write `convergence-latest.json`.
5. Run the private scanner.
6. Review watchlist and decision packet candidates.
7. Promote or demote candidates manually.

Convergence usually does not require hourly refresh. Daily or weekly corpus refresh may be enough, while scanner-side market data can refresh more frequently inside the private runtime.

## 8. Human Review Gate

Trade-relevant outputs must route through human review.

The scanner may surface:

- Candidate themes.
- Candidate tickers.
- Convergence deltas.
- Watchlist rank changes.
- Decision packet candidates.

It must not turn those outputs into live execution from the public corpus.

## 9. Troubleshooting

If the scanner returns no candidates:

- Check that `convergence-latest.json` exists.
- Check that `generated_at` is fresh.
- Check that score rows include `ticker`, `theme`, `score`, `tier`, and `status`.
- Check that theme names match public themes.
- Run `make validate` in `~/trend-corpus`.

If a theme is missing:

- Confirm `trends/<theme>/trend.yaml` exists.
- Confirm the artifact generator includes the same theme.
- Confirm the private runtime registered the theme after validation.

If a packet is blocked:

- Inspect invalidation conditions.
- Check source freshness.
- Check private runtime health summaries.
- Keep the packet gated until a human resolves the issue.
