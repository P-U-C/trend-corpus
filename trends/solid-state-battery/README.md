# Solid-State Battery

This theme tracks public-market exposure to the solid-state lithium battery
transition. Mirrors the pattern of `trends/bitcoin-mining/`: sources -> claims
-> entities -> theses -> decision packets, with sector-tuned half-lives and a
human-review gate before any private execution.

## Sector boundary

In scope:
- U.S.-listed solid-state pure-plays from the 2020-2021 SPAC cohort
  (QuantumScape, Solid Power, SES AI Corp)
- Asian incumbents with announced solid-state programs and mass-production
  roadmaps (Toyota Motor, Samsung SDI, SK Innovation / SK On, LG Energy
  Solution)
- Ceramic separator and component suppliers tied to solid-state scale-up
  (Murata Manufacturing)
- Japanese sulfide-electrolyte and lithium-sulfide suppliers
  (Idemitsu Kosan, Mitsui Mining and Smelting)
- Private keystones whose fundraise marks reprice the listed cohort
  (Factorial Energy, Ampcera, 24M Technologies, Sila Nanotechnologies,
  ProLogium Technology, ION Storage Systems)
- Government policy and incentive flow that changes domestic-cell economics
  (DOE Loan Programs Office, IRA 45X manufacturing credits, USABC programs)

Out of scope:
- Consumer-electronics battery price intelligence
- Lithium upstream mining, refining, and brine economics (separate theme)
- Sodium-ion and other non-lithium chemistries
- EV demand modeling at the OEM finished-vehicle level
- Stationary-storage utility procurement specifics
- Non-public laboratory test data, OEM contract terms, or pre-publication
  cell-design recipes

## Why now

Solid-state batteries crossed three thresholds inside the past six quarters.
First, QuantumScape inaugurated its automated Eagle Line on
2026-02-04 and reported $11.0M of customer billings in Q1 2026, marking the
first sustained customer-billings signal from a U.S. solid-state pure play.
Second, the sulfide-electrolyte supply chain shifted from research-lab
quantities to multi-hundred-ton pilot plants in Japan, with Idemitsu
breaking ground on a sulfide pilot facility in early 2026 and Mitsui
Mining and Smelting scaling its A-SOLiD argyrodite mass-production unit
for 2027 operation. Third, the Asian incumbent roadmaps split into a
2027-2028 first wave (Toyota with Idemitsu; Samsung SDI with BMW and
Solid Power) and later-decade Korean programs (SK On and LG Energy
Solution). The catalyst is the multi-year manufacturing-scale-up clock; the
risk is that electrolyte and separator supply, not cell chemistry, becomes
the binding constraint.

## What's in this directory

- `trend.yaml` -- theme manifest
- `sources/` -- pure-play IR, Asian-incumbent disclosures, Japanese
  sulfide-supplier news, private-keystone press, and DOE / policy feeds
  the runtime ingests
- `claims/` -- 3 example claims demonstrating the category taxonomy
  (regulatory, manufacturing, supply). Illustrative, not pulled from a
  live db.
- `entities/` -- the scanner seeds (QS, SLDP, SES) plus Asian incumbent
  adjacents, Japanese sulfide-electrolyte suppliers, Murata as a
  ceramic-separator ecosystem partner, and private keystones
  (entity_type private_company; no ticker_exposures)
- `events/` -- one example commercial-milestone event
- `theses/` -- the synthesizing argument
- `decision-packets/` -- one watchlist-candidate packet with substantive
  `invalidation_conditions` and `execution_state: human_review_required`
- `watchlists/` -- the operational signals worth monitoring on cadence
- `docs/prompts.md` -- adapted extract / packet / validate prompts with
  solid-state-battery vocabulary

## Sector-tuned half-lives

Solid-state battery developments move on a slow manufacturing-scale-up
clock, with regulatory and corporate cadence sitting on top. The defaults
differ from bitcoin-mining:

| category | half_life_days | why |
|---|---|---|
| regulatory | 90 | DOE LPO awards, IRA 45X interpretive guidance, EU Battery Regulation passports, NHTSA / UNECE battery safety changes |
| corporate | 60 | OEM supply MOUs, JV announcements, fundraise marks, customer-billings disclosures |
| manufacturing | 365 | Eagle Line / Cobra throughput, pilot-line yield, A-sample to B-sample to C-sample transitions |
| market | 365 | EV adoption curves, commercial pilot deployments, automotive design-in windows |
| supply | 180 | sulfide electrolyte and lithium-sulfide capacity, argyrodite tonnage, cathode / silicon-anode availability |
| research | 365 | energy density, cycle life, dendrite suppression, charge-rate benchmarks |

Drop `clinical` and `pricing` entirely -- there is no clinical category in
materials science as we use it, and there is no useful aggregate consumer
price signal yet because shipments are still pilot-scale.

## Reusing this for adjacent themes

This theme is similar in shape to `quantum-computing` and `nuclear-smr`:
emerging-status with a multi-year manufacturing-scale-up clock, a
small number of credible public pure-plays, large incumbents whose
exposure is a slice of mega-cap top lines, and structurally constrained
upstream supply. Future battery-adjacent themes (silicon anode,
sodium-ion, lithium recycling, lithium upstream) should copy this
layout but separate cell-chemistry beta from upstream-mining beta.
