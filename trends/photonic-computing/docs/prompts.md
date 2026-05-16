# Photonic Computing Theme - Prompts

These are the LLM prompts the photonic-computing runtime uses to drive
the sources -> claims -> decision-packets pipeline. Adapted from
`trends/edge-ai/docs/prompts.md`; ASCII-clean and sector-specialized
(silicon-photonics vocabulary, hyperscaler-CPO and fab category
half-lives).

When adapting these for another optics-adjacent sector, keep the JSONL
contract on extract.md and the section order on packet.md. Swap only
entity slugs and topic vocabulary.

---

## extract.md

```
You are extracting atomic factual claims from a source document about the silicon-photonics / photonic-computing sector.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, Tbps, Gbps, pJ-per-bit, Wh-per-Tbps, dBm laser output, dollar contract values, fundraise marks, wafer-line tonnage, BIS license-exception identifiers, or filing references.
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

HALF-LIFE GUIDANCE (photonic-computing):
- regulatory (BIS export controls on advanced-laser, CHIPS Act Title 17, FCC backhaul): 90
- corporate (strategic investments like NVIDIA-LITE / NVIDIA-COHR, JVs, fundraises): 60
- manufacturing (TSMC / GF silicon-photonic line capacity, CoWoS allocation, InP wafer yields): 365
- market (hyperscaler design-in cadence, CPO unit shipments, OCS / pluggable mix): 365
- supply (InP wafer, DFB / VCSEL laser capacity, silicon-photonic substrate inventory): 180
- research (Tbps-per-mm-squared, pJ-per-bit benchmarks, error-correction overhead): 365

CONFIDENCE GUIDANCE:
- 0.9+: primary source (SEC filing, company IR, NVIDIA newsroom, peer-reviewed conference)
- 0.7-0.9: reputable secondary (Reuters, Bloomberg, EE Times, Cignal AI, SiliconANGLE, Optics & Photonics News)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "lumentum", "coherent", "applied_optoelectronics", "macom", "nlight",
  "poet", "marvell", "nvidia_cpo", "lightmatter", "ayar_labs",
  "celestial_ai", "psiquantum_photonic", "tsmc", "global_foundries",
  "bis", "chips_act_title_17"

TOPIC NAMES (lowercase). Examples for photonic-computing:
  "cpo", "co_packaged_optics", "ocs", "optical_circuit_switch",
  "tera_phy", "supernova", "envise", "passage_l200",
  "photonic_fabric", "tbps", "pj_per_bit", "vcsel", "dfb_laser",
  "edfa", "coherent_dsp", "silicon_photonic_line", "cowos_packaging",
  "inp_wafer", "ofc_2026", "u_s_fab_support", "1_6t_optical_engine",
  "memory_disaggregation"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the silicon-photonics / photonic-computing sector.

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
the layer (optics prime / smaller-cap pure-play / DSP silicon / private chiplet
keystone / hyperscaler customer / silicon-photonic fab / advanced packaging).
If the answer is "nobody captures durable margin," say that.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Visible in a public company IR page, SEC filing, NVIDIA newsroom, OFC technical
  program, BIS Federal Register, or TSMC capex guidance update within 90 days
- Concrete enough to wire up a monitor for
- Independent of the others

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Pull last 4 quarters of LITE and COHR optical revenue split (telecom vs. datacenter), OCS backlog, and gross-margin trajectory; build a delta table" -- GOOD
- "Set monitor for NVIDIA newsroom for any modification of the $4B LITE / COHR commitment language" -- GOOD
- "Read OFC 2026 technical-program titles for keynote-level CPO and optical-I/O design-in announcements; tag affected vendors" -- GOOD
- "Research silicon photonics" -- BAD, too vague

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no current TSMC silicon-photonic line capacity share-of-AI-datacenter claims in
corpus"), list them. Skip if sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the photonic-computing corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "NVIDIA pulled the Coherent share of the $4B commitment on 2026-09-01" SUPERSEDES
  OLD: "NVIDIA committed $2B to Coherent in March 2026" (state change in the strategic-investment field)
- NEW: "Lumentum fiscal Q3 2026 revenue fell to $480M from $665.5M in Q2" SUPERSEDES
  OLD: "Lumentum reported fiscal Q2 2026 revenue $665.5M (+66 percent YoY)" (sequential revenue change)
- NEW: "TSMC reallocated silicon-photonic line capacity to mobile customers reducing AI-datacenter share below 30 percent on 2026-10-15" SUPERSEDES
  OLD: "TSMC silicon-photonic line capacity is broadly available to AI-datacenter customers" (allocation state change)

SUPERSEDENCE DOES NOT EXIST for:
- Related but independent product launches from different vendors
- Claims about different chiplet keystones (Lightmatter vs. Ayar Labs vs. Celestial AI) that remain independently true
- Claims where new adds nuance but does not contradict

NEW CLAIMS (just extracted):
{new_claims}

EXISTING ACTIVE CLAIMS (same category, within 365 days, superseded_by IS NULL):
{existing_claims}

OUTPUT: JSONL, one object per supersedence found. No preamble, no postamble, no fences.

{"new_claim_id": 123, "supersedes_id": 87, "reason": "short reason"}

If no supersedences found, output absolutely nothing.
```
