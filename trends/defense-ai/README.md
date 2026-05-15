# Defense AI

This theme tracks public-market exposure to AI / autonomy in defense.
Mirrors the pattern of the canonical `peptides` reference theme:
sources -> claims -> entities -> theses -> decision packets, with
sector-tuned half-lives and a human-review gate before any private
execution.

## Sector boundary

In scope:
- Software / data spines for the warfighter (Palantir, Leidos)
- Defense services integrators with material AI work (Booz Allen,
  CACI, SAIC)
- Autonomous unmanned systems vendors -- public (AeroVironment, Kratos,
  Axon) and private (Anduril, Shield AI, Saronic, Saildrone, Skydio)
- Prime contractors with growing AI / autonomy exposure (LMT, NOC,
  RTX, GD, HII) -- ambiguous purity, treated as low-exposure
- Cross-cutting: Rocket Lab on the defense-launch side (also
  cross-listed in space-satellite)

Out of scope:
- Pure space launch / satcom (separate space-satellite theme)
- Cyber-only vendors (separate emerging theme)
- Pure-software AI without defense customers (covered by ai-infrastructure)
- Classified programs not visible from public budget docs

## Why now

Two structural shifts are running in parallel: the Replicator program
and Mid-Tier Acquisition / OTA pathways are letting nontraditionals
(Anduril, Shield AI) absorb material RDT&E budget faster than primes
can adapt, and the NDAA + DARPA + Joint All-Domain Command and Control
(JADC2 / CJADC2) line items have been growing as a share of total
procurement. The catalyst the trend-corpus checklist names is
"government autonomy contract" -- read that broadly: any visible
inflection in autonomous-systems contract flow toward nontraditionals
prices in fast for the public adjacents.

## What's in this directory

- `trend.yaml` -- theme manifest
- `sources/` -- DoD / regulatory / company IR / trade press feeds the
  runtime ingests
- `claims/` -- 3 example claims demonstrating the category taxonomy
  (regulatory, corporate, market). Illustrative, not pulled from a
  live db.
- `entities/` -- the public scanner seeds (PLTR, LDOS) plus public
  adjacents and 6 private autonomy keystones (entity_type
  private_company; no ticker_exposures)
- `events/` -- one example contract / program event
- `theses/` -- the synthesizing argument
- `decision-packets/` -- one watchlist-candidate packet with
  substantive `invalidation_conditions` and
  `execution_state: human_review_required`
- `watchlists/` -- the operational signals worth monitoring on cadence
- `docs/prompts.md` -- adapted extract / packet / validate prompts
  with defense-AI vocabulary

## Sector-tuned half-lives

Defense moves on procurement and program cycles. The defaults differ
from peptides:

| category | half_life_days | why |
|---|---|---|
| regulatory | 60 | DoD policy, ITAR / AUKUS / export controls move fast |
| corporate | 60 | contract awards are the main signal; arrive on a quarterly cadence |
| manufacturing | 365 | program-of-record manufacturing cycles are multi-year |
| market | 365 | NDAA / RDT&E budget allocations are annual |
| supply | 180 | chips for defense, rare-earth magnets, propellant supply |
| research | 365 | DARPA programs, JADC2 milestones are multi-year |

Drop `clinical` and `pricing` -- defense pricing is contract-specific
and not a useful aggregate signal at this layer.

## Reusing this for adjacent themes

This theme is similar in shape to `nuclear-smr` and `ai-infrastructure`:
single sector with a regulatory backbone + supply-side bottlenecks +
contract-flow signal. Other contract-driven sectors (space-satellite,
biodefense if it became its own theme) would copy this layout.
