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
  (Applied Optoelectronics, MACOM, nLight, POET Technologies)
- Optical-interconnect DSP and switch silicon (Marvell, broadcom
  networking cross-listed with ai-infrastructure)
- Foundry and packaging suppliers whose silicon-photonic line and
  CoWoS-class advanced packaging gate every program (TSMC, GlobalFoundries
  GF Silicon Photonics)
- Privately held photonic-compute and optical-I/O cohort whose
  fundraise marks gate the public revaluation (Lightmatter, Ayar Labs,
  Celestial AI)

Out of scope:
- Free-space optics and LiDAR for automotive (lives in space-satellite
  and robotics-humanoid themes)
- Consumer fiber-to-the-home equipment
- Long-haul telecom-only optics without datacenter interconnect exposure
- Quantum-photonic computing keystones (PsiQuantum) -- cross-listed
  with quantum-computing
- Non-public hyperscaler purchase orders, proprietary fab recipes, or
  CoWoS allocation terms

## Why now

Three structural shifts are running in parallel. First, NVIDIA committed
$4B split equally between Lumentum and Coherent (March 2026) including
equity stakes, multibillion-dollar purchase commitments for advanced
laser components, future capacity access rights, and support for new
U.S.-based fabrication facilities. The investment is the largest
strategic commitment by a hyperscaler-equivalent to silicon photonics
ever announced. Second, the private cohort reached venture milestones
that validate the chiplet-level integration thesis: Lightmatter raised
to $822M total at $4.4B valuation with Passage L200 / L200x optical I/O
above 200 Tbps total bandwidth; Ayar Labs raised $500M Series E at the
end of Q1 2026 bringing total funding to about $870M, with the company
publicly forecasting on-chip optical I/O market maturity in 2026-2028.
Third, the public optical names crossed revenue inflections that align
with hyperscaler scale: LITE fiscal Q2 revenue $665.5M (+66 percent YoY)
with a $400M-plus Optical Circuit Switch backlog and ~166 percent YTD
share-price; COHR fiscal Q3 revenue $1.806B (+21 percent YoY) with
~97 percent YTD. The catalyst is the NVIDIA-anchored CPO buildout plus
private-cohort production-ready chiplets; the risk is hyperscaler
capex pause, silicon-photonic line yield, or competing electrical
solutions (advanced copper, optical engines from in-house ASIC teams).

## What's in this directory

- `trend.yaml` -- theme manifest
- `sources/` -- prime IR, smaller-cap pure-play disclosures, private
  fundraise press, OFC and SIGGRAPH-equivalent technical programs, and
  TSMC capex feeds the runtime ingests
- `claims/` -- 3 example claims demonstrating the category taxonomy
  (corporate, market, supply). Illustrative, not pulled from a live db.
- `entities/` -- the scanner seeds (LITE, COHR) plus optical-component
  adjacents, large-cap incumbents, and 4 private keystones
  (entity_type private_company; no ticker_exposures)
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
keystone fundraise marks (Lightmatter, Ayar Labs, Celestial AI) as
leading catalysts. Future photonics-adjacent themes (defense-photonic,
biophotonic-imaging) should copy this layout but separate hyperscaler-
CPO-driven economics from non-hyperscaler-customer dynamics.
