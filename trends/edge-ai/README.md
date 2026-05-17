# Edge AI

This theme tracks public-market exposure to on-device AI inference
silicon and edge-AI platform software. Mirrors the pattern of
`trends/synthetic-biology/`: sources -> claims -> entities -> theses ->
decision packets, with sector-tuned half-lives and a human-review gate
before any private execution.

## Sector boundary

In scope:
- Pure-play edge-vision and embedded NPU designers (Ambarella,
  Synaptics, Lattice Semiconductor, Mobileye, indie Semiconductor)
- Embedded MCU and analog incumbents with material edge-AI revenue
  exposure (NXP Semiconductors, STMicroelectronics, Texas Instruments)
- Mega-cap semiconductor primes whose edge programs materially shift
  the addressable market (Qualcomm Dragonwing plus the Arduino, Edge
  Impulse, Foundries.io acquisitions; ARM as NPU IP licensor)
- AI accelerator pure-plays whose datacenter-and-edge split is real
  (NVIDIA Jetson exposure, AVGO networking-and-NPU adjacency -- both
  cross-listed with ai-infrastructure)
- Privately-held edge-AI silicon cohort whose fundraise marks reprice
  the public set (Hailo, Mythic, Tenstorrent, SiMa.ai, Untether AI,
  Axelera AI)

Out of scope:
- Cloud-scale training GPU economics (lives in ai-infrastructure)
- Consumer-electronics OEM pricing and unit shipments
- Wireless connectivity standards work (5G / Wi-Fi 7) except where it
  bundles into a specific edge-AI design win
- General-purpose CPU roadmaps without explicit NPU integration
- Intel / AMD / GlobalFoundries as scanner seeds: OpenVINO / Movidius,
  AMD Kria / Xilinx, and GF silicon photonics are real adjacencies, but
  the tradable exposure is too diluted or better captured in
  ai-infrastructure / photonic-computing unless a specific edge-AI
  revenue disclosure appears
- Datacenter-first private accelerators (Groq, Cerebras, Etched, Rivos,
  Esperanto) unless they disclose an edge-specific product ramp or
  automotive / industrial design-in program
- Non-public customer design-in details, RTL, or BIS-controlled
  export-license information

## Why now

Three structural shifts are running in parallel. First, the automotive
L2-plus and L3 design-in window is open and converting: Ambarella has a
quantified roughly $13B fiscal 2027-2032 auto opportunity across won and
invited-to-bid programs, while the higher-end CV3-AD685 program remains
tracked against customer SOP timing rather than treated as already
material production revenue. Mobileye EyeQ6H / SuperVision and indie
vision-processor shipments give the public cohort two additional
automotive edge-AI comparables. Second, on-device generative AI is
reaching commercial edge ramps by 2026: Hailo launched the Hailo-10H
GenAI accelerator (AEC-Q100 Grade 2, 2.5W typical draw) with a 2026
automotive-design production target, Synaptics launched the Astra
multimodal GenAI processor line (SL2610 sampling, Q2 2026 GA), and
Qualcomm launched Dragonwing IQ10 at CES 2026. Third, the platform
consolidation is real: Qualcomm closed five
acquisitions in 18 months (Augentix, Arduino, Edge Impulse, Focus.AI,
Foundries.io) and Lattice Semiconductor signed a $1.65B AMI deal on May
4, 2026, expected to close in Q3 2026. The catalyst is the convergence
of automotive program ramps, on-device GenAI demand, and platform
consolidation; the risk is concentrated leading-edge capacity and
advanced-computing export-control changes, not a fully sourced claim
that edge SoCs are currently being crowded out of TSMC nodes.

## What's in this directory

- `trend.yaml` -- theme manifest
- `sources/` -- chip designer IR, embedded-incumbent disclosures,
  private fundraise press, ARM / TSMC supply commentary, and BIS / FTC
  feeds the runtime ingests
- `claims/` -- 3 example claims demonstrating the category taxonomy
  (corporate, market, supply). Illustrative, not pulled from a live db.
- `entities/` -- the scanner seeds (AMBA, SYNA, LSCC, MBLY, INDI) plus
  embedded incumbent adjacents, mega-cap primes, and 6 private keystones
  (entity_type private_company; no ticker_exposures)
- `events/` -- one example M&A milestone event
- `theses/` -- the synthesizing argument
- `decision-packets/` -- one watchlist-candidate packet with substantive
  `invalidation_conditions` and `execution_state: human_review_required`
- `watchlists/` -- the operational signals worth monitoring on cadence
- `docs/prompts.md` -- adapted extract / packet / validate prompts with
  edge-ai vocabulary

## Sector-tuned half-lives

Edge AI moves on design-in cadence, fundraise marks, and supply-chain
allocation. The defaults differ from synthetic-biology:

| category | half_life_days | why |
|---|---|---|
| regulatory | 90 | BIS export controls on AI chips, FCC / FTC platform-bundle rulings, NHTSA AV rules |
| corporate | 60 | M&A (Lattice-AMI, Qualcomm-Arduino type), partnership deals, fundraise marks |
| manufacturing | 365 | TSMC 5nm / 4nm wafer allocation, advanced packaging (CoWoS), test capacity |
| market | 365 | design-in wins, automotive program ramps, deployment counts, RFQ-to-revenue conversion |
| supply | 180 | HBM allocation, leading-edge wafer slots, substrate / packaging capacity |
| research | 365 | TOPS-per-watt benchmarks, transformer inference efficiency, in-memory compute, sparsity |

Drop `clinical` and `pricing` entirely -- edge silicon has no clinical
category and pricing is design-win-specific.

## Reusing this for adjacent themes

This theme is similar in shape to `ai-infrastructure` and `robotics-
humanoid`: a few credible public pure-plays, large incumbents whose
exposure is a slice of mega-cap top lines, supply-chain dependencies
upstream at TSMC and ASE, and private-keystone fundraise marks as
leading catalysts. Future edge-adjacent themes (industrial-IoT-AI,
in-vehicle-infotainment-AI, robotics-vision-sensors) should copy this
layout but separate transformer-inference TOPS-per-watt benchmarks from
classical CV TOPS-per-watt benchmarks.
