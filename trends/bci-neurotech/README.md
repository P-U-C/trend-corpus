# BCI / Neurotech

This theme tracks public-market and private-market exposure to brain-computer
interfaces and adjacent neuromodulation. Mirrors the pattern of
`trends/bitcoin-mining/`: sources -> claims -> entities -> theses -> decision
packets, with sector-tuned half-lives and a human-review gate before any
private execution.

## Sector boundary

In scope:
- Implantable and minimally invasive BCI companies (Neuralink, Synchron,
  Paradromics, Precision Neuroscience, Blackrock Neurotech, CorTec)
- Non-invasive or lower-invasive BCI entrants and enabling platforms (Merge
  Labs, Forest / Butterfly ultrasound-on-chip)
- Public neuromodulation incumbents with DBS, VNS, spinal-cord stimulation,
  or BCI-linked spinal-cord rehab exposure (BSX, MDT, ABT, LIVN, ONWD)
- Ambiguous scanner seeds adjacent through enabling technology or brain
  biology measurement (BFLY, QSI)
- Peer-reviewed clinical and throughput benchmarks that set the bar for
  device usefulness

Out of scope:
- Neuropsychiatric pharma without device or interface exposure
- General wellness wearables without clinically validated neural-interface
  claims
- Consumer EEG toys and non-medical meditation devices
- Surgical technique, implant programming settings, patient-identifiable data,
  or device exploit details

## Why now

Three structural shifts are running in parallel: FDA IDE and Breakthrough
Device pathways have moved multiple BCI systems into early feasibility or
clinical readout territory; Neuralink, Synchron, Paradromics, Precision, and
Blackrock are creating comparable clinical milestones across different
implant strategies; and Merge Labs / OpenAI plus Forest / Butterfly are
rerating the non-invasive or minimally invasive branch before public
pure-play listings exist. The checklist catalyst is "Neuralink / Synchron /
Merge IPO" -- read that broadly: any visible Neuralink filing, Synchron
commercial-trial step, Paradromics or Precision IDE update, Merge valuation
mark, or neuromod incumbent acquisition can create the first tradable public
BCI cohort.

## What's in this directory

- `trend.yaml` -- theme manifest
- `sources/` -- FDA / ClinicalTrials / company IR / peer-reviewed and official
  investor-source feeds the runtime ingests
- `claims/` -- 3 example claims demonstrating the category taxonomy
  (regulatory, clinical, corporate). Illustrative, not pulled from a live db.
- `entities/` -- the ambiguous scanner seeds (BFLY, QSI) plus public
  neuromod adjacents and private BCI keystones
- `events/` -- one example regulatory / clinical-stage event
- `theses/` -- the synthesizing argument
- `decision-packets/` -- one watchlist-candidate packet with substantive
  `invalidation_conditions` and `execution_state: human_review_required`
- `watchlists/` -- the operational signals worth monitoring on cadence
- `docs/prompts.md` -- adapted extract / packet / validate prompts with
  BCI / neurotech vocabulary

## Sector-tuned half-lives

BCI / neurotech moves on clinical evidence, FDA pathways, private financing,
and implant-manufacturing readiness. The defaults differ from bitcoin-mining:

| category | half_life_days | why |
|---|---|---|
| regulatory | 90 | FDA Breakthrough Device, IDE, EU MDR, and post-market surveillance shape time to pilot |
| corporate | 60 | fundraises, IPO timing, M&A, and partnership marks are the fast private-market clock |
| manufacturing | 365 | implant fabrication, electrode arrays, surgical robotics, and sterile production scale slowly |
| market | 365 | commercial pilot deployments and indication expansion are annual or multi-year signals |
| supply | 180 | medical-grade electrodes, biocompatible polymers, implant electronics, and wireless power are bottlenecks |
| clinical | 3650 | peer-reviewed trial and long-term safety data remain relevant for years |
| research | 365 | channel-count, decoder accuracy, and bandwidth milestones reset technical benchmarks |

Drop `pricing` -- there is no useful consumer price signal yet.

## Reusing this for adjacent themes

This theme is similar in shape to `peptides` on the clinical-evidence side and
to `space-satellite` on the private-keystone side: the public ticker set is
mostly adjacent, while the real signal is still in private clinical milestones,
regulatory status, and first-public-cohort timing.
