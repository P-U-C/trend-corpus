# Photonic Computing

This theme tracks public-market exposure to silicon photonics and the
optical compute-and-interconnect transition. Mirrors the pattern of
`trends/edge-ai/`: sources -> claims -> entities -> theses -> decision
packets, with sector-tuned half-lives and a human-review gate before
any private execution.

## Sector boundary

In scope:
- AI-datacenter optical-interconnect primes now hosting multibillion-
  dollar NVIDIA strategic investments (Lumentum, Coherent)
- Optical-transceiver and InP / silicon-photonic component suppliers
  (Applied Optoelectronics, MACOM, nLight, POET Technologies, Aeluma)
- Optical-interconnect DSP, switching, and CPO platform silicon
  (Marvell with Inphi / Celestial AI / Polariton; Broadcom Tomahawk CPO
  and optical DSP, cross-listed with ai-infrastructure)
- Foundry and packaging suppliers whose silicon-photonic line and
  CoWoS-class advanced packaging gate every program (TSMC,
  GlobalFoundries GF Silicon Photonics, Tower Semiconductor)
- Privately held photonic-compute and optical-I/O cohort whose
  fundraise marks gate the public revaluation (Lightmatter, Ayar Labs,
  Salience Labs)

Out of scope:
- Free-space optics and LiDAR for automotive (lives in space-satellite
  and robotics-humanoid themes)
- Consumer fiber-to-the-home equipment
- Long-haul telecom-only optics without datacenter interconnect exposure
- Quantum-photonic computing keystones (PsiQuantum) -- cross-listed
  with quantum-computing
- Cisco / Acacia and Nokia / Infinera are real optical-networking
  assets but too diluted for this scanner unless datacenter CPO revenue
  or product disclosures become separable
- IPG Photonics is excluded because its current exposure is industrial
  fiber lasers rather than AI-datacenter photonic interconnect
- Black Semiconductor, Quintessent, Optomind, and similar early private
  photonic-compute names remain monitor-only until they disclose a
  datacenter CPO / optical-I/O product, foundry path, or customer ramp
- Non-public hyperscaler purchase orders, proprietary fab recipes, or
  CoWoS allocation terms

## Why now

Three structural shifts are running in parallel. First, NVIDIA committed
$4B split equally between Lumentum and Coherent on March 2, 2026:
$2B to each company, paired with multibillion-dollar purchase
commitments, future access / capacity rights, and U.S.-based
manufacturing support. That is one of the largest public,
customer-anchored silicon-photonics commitments, but not provably the
largest ever across every prior internal hyperscaler, Intel, or foundry
program. Second, the chiplet and CPO platform cohort reached
commercialization milestones: Lightmatter raised $400M in October 2024
at a $4.4B valuation, bringing total capital to $850M, and later
announced Passage L200 / L200x optical I/O above 200 Tbps total
bandwidth; Ayar Labs raised $500M Series E on March 3, 2026, bringing
total funding to $870M at a $3.75B valuation, with high-volume
manufacturing targeted by 2028; Marvell completed the Celestial AI
acquisition on February 2, 2026; and Salience Labs moved AI optical
circuit switching toward pre-production with Tower. Third, the public
optical names crossed revenue inflections that align with hyperscaler
scale: Lumentum reported fiscal Q3 2026 revenue $808.4M (+90 percent
YoY) after fiscal Q2 revenue $665.5M and a $400M-plus Optical Circuit
Switch backlog, while Coherent reported fiscal Q3 2026 revenue $1.806B
(+21 percent YoY). The catalyst is the NVIDIA-anchored CPO buildout
plus private and acquired chiplet platforms moving toward production;
the risk is hyperscaler capex pause, silicon-photonic yield, or
competing electrical / near-package alternatives.

## What's in this directory

- `trend.yaml` -- theme manifest
- `sources/` -- prime IR, smaller-cap pure-play disclosures, private
  fundraise press, OFC and SIGGRAPH-equivalent technical programs, and
  TSMC capex feeds the runtime ingests
- `claims/` -- 3 example claims demonstrating the category taxonomy
  (corporate, market, supply). Illustrative, not pulled from a live db.
- `entities/` -- the scanner seeds (LITE, COHR) plus optical-component
  adjacents, large-cap incumbents, foundry partners, and private /
  acquired chiplet keystones, with ticker exposure only where tradable
- `events/` -- one example strategic-investment event
- `theses/` -- the synthesizing argument
- `decision-packets/` -- one watchlist-candidate packet with substantive
  `invalidation_conditions` and `execution_state: human_review_required`
- `watchlists/` -- the operational signals worth monitoring on cadence
- `docs/prompts.md` -- adapted extract / packet / validate prompts with
  photonic-computing vocabulary

## Sector-tuned half-lives

Photonic computing moves on hyperscaler CPO orders, fab capacity, and
fundraise cadence. The defaults differ from edge-ai:

| category | half_life_days | why |
|---|---|---|
| regulatory | 90 | BIS export controls on advanced laser components, CHIPS Act Title 17 awards, FCC backhaul rules |
| corporate | 60 | strategic investments (NVIDIA-LITE / NVIDIA-COHR type), JVs, fundraise marks, partner deals |
| manufacturing | 365 | TSMC and GF silicon-photonic line capacity, CoWoS allocation, InP wafer yields |
| market | 365 | hyperscaler design-in cadence, CPO unit shipments, OCS / pluggable mix |
| supply | 180 | InP wafer, advanced-laser DFB / VCSEL capacity, silicon-photonic substrate inventory |
| research | 365 | Tbps-per-mm-squared, energy-per-bit benchmarks, error-correction overhead in coherent links |

Drop `clinical` and `pricing` entirely -- photonic computing has no
clinical category and pricing is hyperscaler-design-in-specific.

## Reusing this for adjacent themes

This theme is similar in shape to `quantum-computing` and `ai-
infrastructure`: a few credible public pure-plays, large-cap incumbents
whose photonic exposure is a slice of mega-cap top lines, fab and
advanced-packaging dependencies upstream at TSMC and ASE, and private-
keystone fundraise marks (Lightmatter, Ayar Labs, Salience Labs) plus
acquired platforms (Celestial AI inside Marvell) as leading catalysts.
Future photonics-adjacent themes (defense-photonic,
biophotonic-imaging) should copy this layout but separate hyperscaler-
CPO-driven economics from non-hyperscaler-customer dynamics.
