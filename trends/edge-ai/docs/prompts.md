# Edge AI Theme - Prompts

These are the LLM prompts the edge-ai runtime uses to drive the
sources -> claims -> decision-packets pipeline. Adapted from
`trends/synthetic-biology/docs/prompts.md` (and originally
`trends/bitcoin-mining/`); ASCII-clean and sector-specialized (edge-AI
silicon vocabulary, design-in and supply category half-lives).

When adapting these for another silicon-adjacent sector, keep the JSONL
contract on extract.md and the section order on packet.md. Swap only
entity slugs and topic vocabulary.

---

## extract.md

```
You are extracting atomic factual claims from a source document about the edge-AI silicon / on-device inference sector.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, TOPS, TOPS-per-watt, peak power (W), wafer-node (5nm / 4nm / 7nm), AEC-Q100 grade, design-in customer counts, contract values, fundraise marks, BIS license-exception identifiers, or filing references.
- If the source has no extractable claims (navigation page, error page, pure marketing), output nothing.

OUTPUT FORMAT:
One JSON object per line (JSONL). No preamble, no postamble, no markdown code fences.
Each JSON object must have exactly these fields:

{
  "claim": "single-sentence factual assertion, self-contained",
  "category": "regulatory | corporate | manufacturing | market | supply | research",
  "entities": ["lowercase-slug", ...],
  "topics": ["lowercase-name", ...],
  "date_of_evidence": "YYYY-MM-DD",
  "half_life_days": <int>,
  "confidence": <float 0.0-1.0>
}

HALF-LIFE GUIDANCE (edge-ai):
- regulatory (BIS export controls, FCC / FTC platform bundle, NHTSA AV rules, EU AI Act): 90
- corporate (M&A like Lattice-AMI, partnership deals, fundraise marks, OEM design-in announcements): 60
- manufacturing (TSMC 5nm / 4nm wafer allocation, advanced packaging CoWoS, test capacity): 365
- market (design-in wins, automotive program ramps, deployment counts, RFQ-to-revenue): 365
- supply (HBM allocation, leading-edge wafer slots, substrate / packaging capacity): 180
- research (TOPS-per-watt benchmarks, transformer inference efficiency, in-memory compute, sparsity): 365

CONFIDENCE GUIDANCE:
- 0.9+: primary source (SEC filing, company IR, BIS Federal Register, peer-reviewed conference)
- 0.7-0.9: reputable secondary (Reuters, Bloomberg, EE Times, SemiAnalysis, SiliconANGLE, AnandTech)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "ambarella", "synaptics", "lattice", "qualcomm", "arm", "nxp",
  "stmicro", "ti", "nvidia_jetson", "hailo", "mythic", "tenstorrent",
  "sima_ai", "untether_ai", "bis", "tsmc", "continental", "bosch"

TOPIC NAMES (lowercase). Examples for edge-ai:
  "cv3_ad685", "cv5", "cv7", "n1", "astra_sl2610", "ethos_npu",
  "cortex_m", "cortex_a", "stm32n6", "neural_art", "x_cube_ai",
  "sitara_am6", "imx_95", "s32", "dragonwing_iq10", "arduino",
  "edge_impulse", "foundries_io", "hailo_10h", "aec_q100", "ami_acquisition",
  "auto_pipeline", "tops_per_watt", "transformer_inference",
  "in_memory_compute", "analog_compute", "cowos_packaging", "5nm",
  "bis_entity_list", "license_exception", "design_in_window"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the edge-AI silicon sector.

THE USER is a sophisticated investor / builder with zero appetite for hedging,
generic disclaimers, or "on one hand, on the other" waffling. They want a ranked,
opinionated answer backed by the evidence below, with specific actions they can take today.
They are the filter on your output -- your job is to produce packets fast enough that they
can say yes or no quickly.

QUESTION: {question}
GENERATED: {date}

EVIDENCE BASE (active claims only, most recent first, max 200):
{claims}

OUTPUT: markdown document, starting with the title line below, using these exact sections
in this exact order. Do not wrap the output in code fences.

# Decision Packet: {question}
*Generated: {date}*

## Verdict
One of: **PURSUE**, **WATCH**, **AVOID**, **KILL**. One sentence justifying it.

## Why now
3-5 bullets on the specific catalysts making this question live today. Each bullet must
reference at least one claim by ID in square brackets, e.g. [C-42]. Each bullet must be
a concrete, dated fact -- not a generalization.

## What the evidence actually says
A tight synthesis of the relevant claims. Cite claim IDs inline like [C-42, C-87].
Flag contradictions explicitly. Explicitly call out any load-bearing claim with confidence <0.6.

## Who captures the margin
2-3 sentences on where value accrues given this specific question. Be specific about
the layer (pure-play edge silicon / large-cap platform / embedded MCU incumbent /
IP licensor / private accelerator / TSMC supply / CoWoS packaging / reference-design
software stack). If the answer is "nobody captures durable margin," say that.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Visible in a public company IR page, SEC filing, BIS Federal Register, NHTSA
  docket, EE Times / SemiAnalysis briefing, or TSMC capex guidance update within 90 days
- Concrete enough to wire up a monitor for
- Independent of the others

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Pull last 4 quarters of AMBA auto-pipeline awarded-to-revenue conversion, Continental / Bosch design-in disclosures, and CV3-AD revenue ramp; build a delta table" -- GOOD
- "Set monitor for BIS Federal Register notices on advanced-computing export controls touching AI chips" -- GOOD
- "Read latest Lattice 10-Q section on AMI integration plan plus Qualcomm Dragonwing IQ10 design-in disclosures" -- GOOD
- "Research AI chips" -- BAD, too vague

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no current TSMC edge-node wafer-allocation share-of-capacity claims in corpus"),
list them. Skip if sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the edge-ai corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "Ambarella reduced the published auto opportunity pipeline to $9B fiscal 2027-2032 on 2026-08-01" SUPERSEDES
  OLD: "Ambarella auto opportunity pipeline is ~$13B fiscal 2027-2032" (state change at the headline number)
- NEW: "Lattice Semiconductor abandoned the AMI acquisition on 2026-09-15" SUPERSEDES
  OLD: "Lattice signed a $1.65B definitive agreement to acquire AMI expected to close Q3 2026" (transaction outcome change)
- NEW: "BIS issued a license exception broadening China-bound shipments of edge AI chips below 70 TOPS on 2026-10-01" SUPERSEDES
  OLD: "BIS export controls materially affect China-bound shipments of edge-AI silicon above 50 TOPS" (regulatory state change)

SUPERSEDENCE DOES NOT EXIST for:
- Related but independent design-in updates from different developers
- Claims about different end markets (automotive vs. smart-home vs. industrial vision) that remain independently true
- Claims where new adds nuance but does not contradict

NEW CLAIMS (just extracted):
{new_claims}

EXISTING ACTIVE CLAIMS (same category, within 365 days, superseded_by IS NULL):
{existing_claims}

OUTPUT: JSONL, one object per supersedence found. No preamble, no postamble, no fences.

{"new_claim_id": 123, "supersedes_id": 87, "reason": "short reason"}

If no supersedences found, output absolutely nothing.
```
