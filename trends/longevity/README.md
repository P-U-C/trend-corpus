# Longevity

This theme tracks public-market exposure to the longevity and biological-
aging therapeutics sector. Mirrors the pattern of `trends/synthetic-
biology/`: sources -> claims -> entities -> theses -> decision packets,
with sector-tuned half-lives and a human-review gate before any private
execution.

## Sector boundary

In scope:
- Small public near-pure-play universe (BioAge Labs as the most
  credible US-listed pure play; Unity Biotechnology as the distressed
  senolytic precedent now in wind-down)
- AI-bio longevity adjacency that listed on HKEX (Insilico Medicine)
- Large-cap pharma whose longevity exposure is investor or acquirer
  optionality rather than a P-and-L driver (AbbVie post-Calico exit,
  Alphabet as Calico parent, Eli Lilly as NewLimit investor plus GLP-1
  obesity halo, Novo Nordisk via GLP-1)
- Privately-held longevity cohort whose fundraise marks and pre-clinical
  milestones lead the public revaluation (Altos Labs, Calico Life
  Sciences, Loyal, Retro Biosciences, NewLimit, Life Biosciences,
  Rejuvenate Bio)

Out of scope:
- General oncology and immunology pipelines without a stated longevity
  or healthspan hypothesis
- Cosmetic anti-aging and aesthetic dermatology
- Nutraceutical supplement brands
- Consumer wellness wearables and biological-age tests
- Non-public IND data, off-label prescribing data, or proprietary
  cell-reprogramming recipes

## Why now

Three structural shifts run in parallel. First, partial epigenetic
reprogramming entered human clinical trials in 2026 when Life
Biosciences' ER-100 received FDA IND clearance for optic neuropathies.
AI-engineered proteins achieved more than 50x increased expression of
stem-cell reprogramming markers via the
Retro Biosciences and OpenAI collaboration. Second, the venture marks
in the private cohort hit institutional scale: NewLimit raised $130M
Series B plus $45M follow-on from Eli Lilly, Section 32, and Duke
Management at a $1.62B valuation; Altos Labs remains a $3B-funded
preclinical private keystone; Loyal received FDA RXE acceptance for
LOY-002 in 2025 and completed two of three major technical sections
toward expanded conditional approval by early 2026. Third, the public surface
contracted at the same time: AbbVie ended its 11-year, ~$3.5B Calico
partnership in November 2025 over a strategy pivot to genetic
medicines; Unity Biotechnology stockholders approved liquidation in
September 2025 after UBX1325 narrowly missed a Phase 2b primary
endpoint. The catalyst is clinical-trial-first-readouts for partial
reprogramming therapies and the BioAge Labs BGE-102 NLRP3 and APJ
agonist program cadence; the risk is binary regulatory outcomes,
the narrow public investable surface, and the historical record of
near-zero successful translation from animal lifespan extension to
human longevity endpoints.

## What's in this directory

- `trend.yaml` -- theme manifest
- `sources/` -- developer IR, AbbVie / Alphabet news, private fundraise
  press, peer-reviewed longevity studies, FDA CDER / CBER, clinicaltrials.gov
- `claims/` -- 3 example claims demonstrating the category taxonomy
  (clinical, corporate, research). Illustrative, not pulled from a live
  db.
- `entities/` -- the scanner seed (BIOA) plus distressed precedent
  (UBX), large-cap adjacents (ABBV, GOOGL, LLY, NVO), HKEX-listed
  AI-bio (Insilico Medicine), and 7 private keystones (entity_type
  private_company; no ticker_exposures)
- `events/` -- one example partnership-end / strategy-pivot event
- `theses/` -- the synthesizing argument
- `decision-packets/` -- one watchlist-candidate packet with substantive
  `invalidation_conditions` and `execution_state: human_review_required`
- `watchlists/` -- the operational signals worth monitoring on cadence
- `docs/prompts.md` -- adapted extract / packet / validate prompts with
  longevity vocabulary

## Sector-tuned half-lives

Longevity moves on FDA review cycles, peer-reviewed clinical readouts,
private fundraise cadence, and large-cap M&A flow. The defaults differ
from synthetic-biology but are close because the regulatory and
clinical machinery is largely shared:

| category | half_life_days | why |
|---|---|---|
| regulatory | 90 | FDA RMAT / IND clearance for partial reprogramming, ICH guidance on aging clinical endpoints, FDA AERS surveillance |
| corporate | 60 | partnership end events (AbbVie-Calico type), fundraise marks, IPO calendar, large-cap acquirer optionality |
| manufacturing | 365 | AAV vector capacity, cell-therapy GMP capacity for reprogramming approaches, small-molecule CMO |
| market | 365 | commercial revenue once anything ships (largely future), DOC pet-therapy revenue (Loyal as the only commercial signal) |
| supply | 180 | mRNA / lipid nanoparticle reagents, viral vectors, cellular-reprogramming TF reagents |
| clinical | 3650 | peer-reviewed trial readouts -- the longest half-life category; an aging-endpoint trial result is structural |
| research | 365 | new aging biomarkers (epigenetic clocks, GrimAge / PhenoAge), reprogramming techniques, senolytic chemistry |

Keep `clinical` (peer-reviewed trial readouts are the most durable
signal in this sector) and drop `pricing` (no commercial pricing yet).

## Reusing this for adjacent themes

This theme is similar in shape to `synthetic-biology`: clinical-stage
drivers, FDA-led regulatory pacing, foundry-and-supply dependencies, and
a mix of small-cap public, large-cap incumbent partner or acquirer, and
private-keystone catalysts. The longevity-specific distinction is that
the public investable surface is unusually thin (one near-pure-play in
BioAge, one distressed precedent in Unity) and binary - so the watchlist
weights private-keystone trial readouts and GOOGL / LLY / NVO
optionality more heavily than in synthetic-biology.
