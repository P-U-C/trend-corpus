# Sector-Aggregates → Scanner Bridge: Implementation Plan

**Status:** plan only — not yet executed. Send back any objections before
Phase 1 starts.

**Context:** the peptide runtime publishes daily aggregates into
`trend-corpus/trends/peptides/aggregates/peptides-aggregates.json`,
which feeds the opportunity-generator + convergence merger and lands in
the public scanner at `pft.permanentupperclass.com/scanner/`. The 13
sector runtimes deployed on `city-worker-301` (ai-infrastructure,
quantum-computing, nuclear-smr, robotics-humanoid, defense-ai,
space-satellite, bitcoin-mining, bci-neurotech, solid-state-battery,
synthetic-biology, edge-ai, photonic-computing, longevity) do NOT
publish aggregates. The scanner dashboard has been stale since
2026-04-28 because nothing past peptides ever reaches it.

This plan closes that gap.

## Current state (post-audit)

```
                                                            ┌──────────────────┐
city-worker (peptide user) ── scp ──→ orchestration box ──→ │ trend-corpus     │
                                                            │ trends/peptides/ │
                                                            │  aggregates/     │
                                                            └──────────────────┘
                                                                    │
                                                                    ▼
                                                            ┌──────────────────────┐
                                                            │ trend-intel-private  │
                                                            │ themes/peptides/     │
                                                            │  opportunity-rows    │
                                                            └──────────────────────┘
                                                                    │
                                                                    ▼
                                                            ┌──────────────────────┐
                                                            │ puc-trading/corpus/  │
                                                            │ convergence-         │
                                                            │   latest.json        │
                                                            └──────────────────────┘
                                                                    │
                                                                    ▼
                                                            ┌──────────────────────┐
                                                            │ scanner / public     │
                                                            │ dashboard            │
                                                            └──────────────────────┘
```

Pieces today:
1. `/home/peptide/peptide-corpus/scripts/export-public-aggregates.py` —
   hardcoded `THEME_ID="peptides"`, peptide-specific `top_peptides`
   field, reads `~/peptide-corpus/db.sqlite` read-only, emits
   `peptides-aggregates.json`.
2. `~/pf-scout-bot/deploy/sync-peptides-aggregates.sh` — scp from
   `city-worker-peptides:/var/lib/peptide-public/`, schema-validates
   against `aggregates.schema.json`, secret-scans, commits, optionally
   pushes.
3. `~/trend-intel-private/scripts/generate_opportunities.py` — reads
   YAMLs from `~/trend-intel-private/themes/peptides/{claims,entities,
   sources}/`, weighted scoring, emits `opportunity-rows.json`. Today
   only peptides has a directory under `trend-intel-private/themes/`.
4. `~/puc-trading/corpus/merge_convergence.py` — defaults are hardcoded
   to peptides paths but accepts `--opportunity-source` flag.
5. `~/puc-trading/corpus/convergence-latest.json` — already populated
   from fixture seed (`populate_convergence.py`) for many sector themes,
   but the merge-flow only updates peptides today.

## Plan

### Phase 1 — Generic aggregates exporter in `theme_runtime` (1-2h)

Add `theme_runtime export-aggregates` subcommand to the shared runtime
package on `clawd:~/trend-corpus/runtime/theme_runtime/`.

Spec:
- Reads from local SQLite (claims + sources tables) — same read-only
  pattern as the peptide exporter.
- Theme-agnostic: pulls `theme_id` + generator metadata from
  `theme-config.yaml`.
- Computes rolling windows: 30d / 90d / 365d (same as peptide).
- Per window: `claims_total`, `claims_by_category`,
  `top_entities` (slug + mentions), suppressed below `min_count_threshold`.
- Omits the peptide-specific `top_peptides` field unless `peptide`
  appears in `claim_categories` (peptide-only, never trips for sectors).
- Outputs to `<root>/out/<theme-id>-aggregates.json` by default,
  configurable via `--out`.
- Schema-validates the payload against
  `trend-corpus/schemas/aggregates.schema.json` before write.
- Tests: 4-5 unit tests covering empty db, non-empty windows, suppression
  threshold, peptide-vs-sector schema branch.

Files added:
- `runtime/theme_runtime/aggregates.py`
- `runtime/theme_runtime/__main__.py` — wire `export-aggregates` subcommand
- `runtime/theme_runtime/tests/test_aggregates.py`

No changes to the existing peptide exporter; it stays as the
peptide-host reference until peptide gets cut over to the generic one.

### Phase 2 — Self-publishing from each runtime user (1-2h)

Two options for getting aggregates from the city-worker runtime users
into the public `trend-corpus`. Default to (a); fall back to (b) if you
prefer the air-gap discipline.

**Option (a) — runtime users push directly** (recommended):

Each runtime user on city-worker already has a `trend-corpus/` checkout
(used by the 05:00 UTC `sync` cron). Adding push capability:
1. Issue a fine-grained PAT scoped to `P-U-C/trend-corpus` contents:write.
2. Configure each runtime user's `trend-corpus/.git/config` with the
   token-embedded remote URL (mirrors the pattern used for pft-validator).
3. New cron entry per runtime:
   ```
   30 13 * * * <user> cd ~/<theme>-corpus && bash ~/trend-corpus-runtime/templates/cron-wrap.sh export-aggregates --commit-and-push >> ~/logs/<theme>-aggregates.log 2>&1
   ```
   Fires at 13:30 UTC, 30 min before the daily digest at 14:00 UTC.
4. Stagger by user (offset +60s per theme) to avoid 14 concurrent
   pushes on the same remote.

Pros: simpler, no scp glue, no permissions-juggling, no separate sync
script. The runtime that knows the most about its data is the one that
publishes it.

Cons: each runtime user holds a push token. Compromised runtime user =
compromised public corpus (mitigated by branch protection + the existing
trend-corpus CI validator rejecting bad commits).

**Option (b) — orchestration box pulls** (mirrors peptide pattern):

Same as today for peptide, but generalized:
1. Each runtime user writes aggregates to `/var/lib/<user>-public/`.
2. `scripts/sync-theme-aggregates.sh --theme <slug>` on orchestration
   box pulls all 14 themes via scp, validates, commits, pushes.
3. Single cron entry on orchestration box.

Pros: runtime users stay read-only against trend-corpus.

Cons: needs `/var/lib/<user>-public/` + group permissions per user,
needs ubuntu user added to each user's group, needs a sync script that
handles 14 themes serially.

### Phase 3 — Trend-corpus aggregates validation (30 min)

Today the corpus validator does not walk `aggregates/` directories. The
peptide sync script schema-checks inline. For consistency:

1. Extend `corpus_validator/validator.py` to recognize
   `trends/<theme>/aggregates/<theme>-aggregates.json` and validate
   against `schemas/aggregates.schema.json`.
2. Add tests: a clean aggregates file passes; a malformed one (missing
   `theme_id`, mismatched theme_id, wrong type) fails.
3. Update Makefile / docs to note that `make validate` now covers
   aggregates as well.

This means a runtime user can't push a malformed aggregates JSON because
the local pre-push validate would catch it AND the trend-corpus CI
runs validate on every PR / push.

### Phase 4 — Opportunity-generator over public corpus (30 min)

The existing generator reads from `~/trend-intel-private/themes/<slug>/`
which only has `peptides` today. Simplest path forward:

1. Run `generate_opportunities.py --theme <slug> --themes-dir ~/trend-corpus/trends/`
   directly. The generator already accepts `--themes-dir` so this works
   without code changes, provided each theme has the expected directory
   shape (claims/, entities/, sources/, opportunity-config.yaml).
2. **Each sector theme needs an `opportunity-config.yaml`** — currently
   missing. Add one per theme with sensible weights (mostly copy peptide
   defaults; tune `lookback_days` per the theme's half-life category).
3. Output to `~/trend-intel-private/themes/<slug>/artifacts/opportunity-rows.json`
   (create the directory shell — opportunity-rows is private semi-public
   data, lives under trend-intel-private).
4. Alternative: leave the public corpus untouched and create
   `~/trend-intel-private/themes/<slug>/` shells that symlink claims/
   entities/sources to the public corpus + add opportunity-config.yaml
   locally. Cleaner separation of public-data vs. private-tuning.

Recommended: **add `opportunity-config.yaml` to each public theme dir**
(it's tuning, not data), point the generator at public trend-corpus
directly with `--themes-dir`. trend-intel-private remains for genuinely
private extensions (e.g. private peptide claims).

### Phase 5 — Merger over all themes (30 min)

`merge_convergence.py` accepts `--opportunity-source` flag. New
orchestration wrapper iterates all 14 themes:

```bash
# scripts/refresh-convergence.sh
for theme in peptides ai-infrastructure quantum-computing nuclear-smr \
             robotics-humanoid defense-ai space-satellite bitcoin-mining \
             bci-neurotech solid-state-battery synthetic-biology edge-ai \
             photonic-computing longevity; do
    python3 ~/puc-trading/corpus/merge_convergence.py \
        --opportunity-source ~/trend-intel-private/themes/$theme/artifacts/opportunity-rows.json \
        --out ~/puc-trading/corpus/convergence-latest.json
done
```

Then commit + push convergence-latest.json into puc-trading so the
scanner picks it up.

### Phase 6 — End-to-end validation (1h)

Walk one theme through the entire chain manually before any cron is enabled:

1. Run `theme_runtime export-aggregates` on city-worker as `ai-infra` user.
2. Confirm `~/ai-infra-corpus/out/ai-infrastructure-aggregates.json` is
   schema-valid + secret-clean.
3. Commit + push via the runtime user's push token; verify it lands at
   `P-U-C/trend-corpus:trends/ai-infrastructure/aggregates/`.
4. On orchestration box: `git pull trend-corpus`, run
   `generate_opportunities.py --theme ai-infrastructure`, verify
   `opportunity-rows.json` is produced.
5. Run `merge_convergence.py`, verify `convergence-latest.json` now has
   ai-infrastructure entries alongside peptides.
6. Push puc-trading, verify scanner refreshes.

If all green, repeat for one more theme. Then enable crons for all 14.

### Phase 7 — Cron orchestration + runbook (1h)

1. Per-runtime cron on city-worker (Option (a)): 14 `export-aggregates`
   entries staggered 13:30 + 1 min offset per theme.
2. Orchestration-box cron on clawd:
   - 13:55 UTC: `git pull` trend-corpus (catch all aggregates pushes)
   - 14:00 UTC: run opportunity-generator over all 14 themes (existing
     digest cron already fires runtime digests at 14:00; the generator
     work piggy-backs).
   - 14:05 UTC: run merger over all 14 themes, write convergence-latest.
   - 14:10 UTC: commit + push convergence-latest to puc-trading.
3. Runbook updates:
   - `ops/runbooks/peptides-aggregates-bridge.md` → rename to
     `aggregates-bridge.md`, generalize to "any-theme" language.
   - `ops/runbooks/install.md` → add the per-runtime push-token step
     to the bring-up sequence (extends task #43).
   - New: `ops/runbooks/scanner-feed.md` — end-to-end overview from
     runtime → scanner with cron timings.

## Risk register

| Risk | Mitigation |
|---|---|
| 14 concurrent git-pushes race | Stagger per-theme cron by +60s; retries on `non-fast-forward` rejection in cron-wrap |
| Bad aggregates JSON makes scanner go blank | Pre-push validate + trend-corpus CI validate; merger is additive (peptide stays even if sectors break) |
| Push token compromise on a runtime user | Fine-grained PAT scoped only to `trend-corpus` contents:write; trend-corpus CI catches schema violations; revoke + rotate procedure documented |
| Schema drift between exporter and validator | Single source of truth: `schemas/aggregates.schema.json`. Both exporter and validator read from this; unit tests cover round-trip |
| Empty SQLite (no extracts yet) → empty aggregates | Exporter emits valid empty-state JSON; merger treats it as no-op for that theme |
| Opportunity-generator chokes on a theme missing `opportunity-config.yaml` | Phase 4 adds configs first; CI checks every theme dir has one |

## Out of scope (deferred)

- Private extensions for sector themes (`trend-intel-private/themes/<sector>/`
  beyond opportunity-config). Add when there's actually private data to
  extend with.
- Real-time push (websockets etc). Daily is the right cadence for
  the current data velocity.
- Backfill historical aggregates. The first push at 13:30 UTC will be
  the new baseline.

## Decision points before I start

1. **Option (a) vs. (b) for publishing** — runtime users push directly
   (default recommendation) vs. orchestration-box pulls. Risk is in the
   table above; (a) is faster to deploy.
2. **Opportunity-configs in public corpus vs. private mirror** — I'd
   put them in public `trend-corpus/trends/<slug>/opportunity-config.yaml`
   because they're tuning, not data. If you want a clean
   private/public split kept, I'll put them in
   `trend-intel-private/themes/<slug>/` instead.
3. **Cadence** — daily at 13:30/14:00 UTC matches existing digest cron.
   If sector data velocity says weekly is better, easy to change.

## Estimate

- Phase 1: 1-2h (code + tests)
- Phase 2 + Phase 3 + Phase 4: 1-2h
- Phase 5 + Phase 7: 1h
- Phase 6: 1h
- **Total clock time: ~5-6 hours of focused work, end-to-end on one
  theme then fan out to all 13.**

If you greenlight, I start at Phase 1.
