# Synthetic Biology

This theme tracks public-market exposure to the engineered-biology sector.
Mirrors the pattern of `trends/solid-state-battery/`: sources -> claims ->
entities -> theses -> decision packets, with sector-tuned half-lives and a
human-review gate before any private execution.

## Sector boundary

In scope:
- CRISPR and base-editing clinical-stage and commercial-stage developers
  (CRISPR Therapeutics, Beam Therapeutics, Intellia Therapeutics, Editas
  Medicine, Caribou Biosciences)
- Cell-engineering, DNA-synthesis, and protein-engineering foundries
  (Ginkgo Bioworks, Twist Bioscience, Codexis)
- Sequencing incumbents whose technology gates discovery cadence
  (Pacific Biosciences, Illumina)
- AI-bio drug discovery adjacents whose 2026-2027 readouts are the
  cross-sector validation events (Recursion Pharmaceuticals, Schrodinger)
- Large-cap commercial partners and acquirers materially exposed to the
  sector (Vertex Pharmaceuticals as Casgevy commercial lead, Eli Lilly
  post-Verve acquisition)
- Private keystones whose milestone announcements reprice the public
  cohort (Scribe Therapeutics, Mammoth Biosciences, Synthego, Inscripta)

Out of scope:
- Traditional small-molecule oncology and immunology pipelines
- Vaccine platforms without explicit synthetic-biology editing chemistry
- Diagnostics not connected to engineered-biology workflows
- Agricultural and industrial-biotech feedstock pricing
- Non-public patient data, proprietary cell-line recipes, gain-of-function
  research protocols, or non-public BLA / IND submission contents

## Why now

Three structural shifts run in parallel. First, commercial revenue from
one-time gene therapies has crossed thresholds: CRISPR Therapeutics
reported Q1 2026 Casgevy revenue of $43M and more than 500 patients
initiated treatment, with full-year 2025 revenue of $116M and a $2B cash
position. Second, the base-editing and in-vivo cohort has multiple
near-term readouts: Beam BEAM-302 in alpha-1 antitrypsin, Verve VERVE-102
LDL cholesterol data (now under Eli Lilly ownership after a June 2025
acquisition), Intellia in vivo CRISPR for transthyretin amyloidosis,
Editas seeking a partner for reni-cel. Third, the AI-bio adjacents reach
Phase III in 2026 (Schrodinger zasocitinib), forming the first
large-scale clinical test of whether AI-aided design produces durable
better outcomes. The catalyst is commercial-revenue compounding plus
2026 indication-expansion calendar; the risk is one-time-therapy ceiling
economics and the supply-chain bottleneck of AAV vector and viable cell
collection at GMP grade.

## What's in this directory

- `trend.yaml` -- theme manifest
- `sources/` -- developer IR, foundry IR, sequencing-incumbent feeds,
  AI-bio updates, FDA / NIH / OSTP policy feeds the runtime ingests
- `claims/` -- 3 example claims demonstrating the category taxonomy
  (clinical, corporate, supply). Illustrative, not pulled from a live db.
- `entities/` -- the scanner seeds (CRSP, BEAM, NTLA) plus pure-play
  adjacents and 4 private keystones (entity_type private_company; no
  ticker_exposures)
- `events/` -- one example commercial-milestone event
- `theses/` -- the synthesizing argument
- `decision-packets/` -- one watchlist-candidate packet with substantive
  `invalidation_conditions` and `execution_state: human_review_required`
- `watchlists/` -- the operational signals worth monitoring on cadence
- `docs/prompts.md` -- adapted extract / packet / validate prompts with
  synthetic-biology vocabulary

## Sector-tuned half-lives

Synthetic biology moves on FDA review cycles, peer-reviewed clinical
readouts, and corporate fundraise / M&A cadence. The defaults differ from
solid-state-battery:

| category | half_life_days | why |
|---|---|---|
| regulatory | 90 | FDA BLA / IND / RMAT / breakthrough designations, CDC select-agent rules, EU EMA pathway updates |
| corporate | 60 | M&A (Lilly-Verve type), partnership deals, fundraise marks, Vertex-CRSP profit-share updates |
| manufacturing | 365 | AAV vector capacity, cell-collection (CD34+) GMP scale, plasmid manufacture, cleanroom capex |
| market | 365 | patient initiations, indication expansion, commercial revenue trajectory, payer coverage |
| supply | 180 | gRNA, sgRNA, plasmid, AAV, viral-vector lots, custom-DNA synthesis backlog |
| clinical | 3650 | peer-reviewed trial readouts -- the longest half-life category; an approval is structural |
| research | 365 | new editing platforms (prime, twin prime, epigenetic), delivery breakthroughs (LNP, AAV alternatives) |

Keep `clinical` (peer-reviewed trial results are the most durable signal
in this sector) and drop `pricing` (one-time gene-therapy pricing is too
case-specific to aggregate as a useful signal yet).

## Reusing this for adjacent themes

This theme is similar in shape to `bci-neurotech` and `peptides`:
clinical-stage drivers, FDA-led regulatory pacing, foundry / supply-chain
dependencies, and a mix of pure-play public, large-cap incumbent partner,
and private-keystone catalysts. Future biology-adjacent themes (longevity,
mRNA platforms, cell therapy 2.0) should copy this layout but separate
gene-editing chemistry-specific signals from delivery-platform-specific
signals.
