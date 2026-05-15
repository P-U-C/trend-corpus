# Peptides Theme Walkthrough

The peptides theme at `trends/peptides/` is the canonical reference for the
trend-corpus pattern. This walkthrough explains what is in it and how the
pieces fit, so new themes can copy the shape with confidence.

## The pipeline

```
sources --(ingest, periodic)--> raw_text --(extract, Sonnet)--> claims (append-only)
                                                                  |
                                                                  v
                                                  packet.py (Opus, on demand) --> decision packet
                                                                  |
                                                                  +-- supersedence check (validate.md) --+
                                                                                                         v
                                                                                            superseded_by pointers set
```

The runtime that proves the pattern uses SQLite + WAL, OAuth via Claude Code
CLI (subscription auth, not API key), and a `fresh_claims` SQL view that
filters non-superseded claims still within their category's half-life.

## The objects in `trends/peptides/`

### `trend.yaml`

The theme manifest. Declares status (`peak_hype` for peptides today), schema
version, the public safety boundary (the theme is for market and infrastructure
analysis, not medical or procurement advice), and which object folders exist.

### `sources/` (12 objects)

One source object per upstream URL the runtime ingests. Three source types are
represented:

- `regulatory_primary`: FDA drug-alerts, drug-shortages, advisory-committee
  calendar, Health Canada drugs portal.
- `company_ir`: Bachem, PolyPeptide, Lilly, Novo, Hims investor relations.
- `trade_press`: Endpoints obesity feed, FiercePharma RSS, STAT obesity.

Each source object pins a `url`, `type`, `title`, `accessed_at`, and a brief
`notes` field explaining what claims the source is suited for. The runtime's
ingest script reads the same URLs; the YAML objects are the public-facing
inventory.

### `claims/` (3 example objects)

The claim examples demonstrate the taxonomy without leaking the live
database's actual claim history:

- `clm_glp1_manufacturing_capacity_bottleneck` (category: `manufacturing`,
  half-life 180): supply-side thesis backed by CDMO and originator IR.
- `clm_fda_compounding_enforcement_shift` (category: `regulatory`, half-life
  90): the structural rule that 503A and 503B compounding rights depend on
  FDA shortage status.
- `clm_telehealth_compounded_glp1_volume` (category: `market`, half-life 365):
  the downstream demand-side signal observable in DTC telehealth IR.

Each claim has `source_ids`, `date_of_evidence`, `category`, and `confidence`.
Confidence follows the rubric in `docs/prompts.md` extract-prompt section:
0.9+ for primary, 0.7-0.9 for reputable secondary, 0.5-0.7 for trade press.

### `entities/` (3 objects)

`ent_lilly`, `ent_novo`, `ent_bachem` use the entity-slug convention
(short lowercase) and include tickers, exchanges, and a short `role` array.
The runtime uses entity slugs to join claims to entities.

### `events/` (1 example)

`evt_example_capacity_expansion` is illustrative: a CDMO capacity announcement
linked to the relevant entity and claim. Real events would be timestamped
runtime observations.

### `theses/` (1 object)

`ths_peptide_manufacturing_picks_and_shovels`: the synthesizing argument that
CDMO exposure is a cleaner picks-and-shovels trade than originator equities,
backed by the three example claims.

### `decision-packets/` (1 object)

`dp_peptide_manufacturing_watchlist`: a watchlist-candidate verdict with
`execution_state: human_review_required` and four substantive
`invalidation_conditions`. This is the kind of object a metalayer would emit
and a human would gate before any private execution.

### `watchlists/` (1 object)

`wl_peptide_manufacturing_exposure`: the operational shape of what to monitor
on a cadence -- CDMO capex, FDA shortage status, originator capex, compounding
enforcement, DTC volume.

### `docs/prompts.md`

The three live runtime prompts (`extract`, `packet`, `validate`), verbatim
with ASCII-only conversion. These are the highest-leverage artifact to reuse
when spinning up a new sector. See `docs/new-sector-research-workflow.md`.

## What is NOT here

- No live `db.sqlite` claim history.
- No generated decision packets that reference real positions.
- No credentials.
- No operator-specific context.

The runtime stays private; this theme publishes the methodology.

## Reusing the pattern for a new sector

1. Copy `trends/_template/` into `trends/<your-sector>/`.
2. Replace `trend.yaml` fields with sector-appropriate values.
3. Inventory 8-15 upstream URLs; emit a source object per URL.
4. Define 2-3 entities using the entity-slug convention.
5. Identify 3-5 example claims that demonstrate the category taxonomy.
6. Synthesize one thesis and one decision packet with substantive
   `invalidation_conditions` and `execution_state: human_review_required`.
7. Paraphrase the three prompts in `trends/peptides/docs/prompts.md` for your
   sector's vocabulary.
8. Run `make validate` and `make test` until both pass.

For the agent-driven version of this workflow, see
`docs/new-sector-research-workflow.md` at the repo root.
