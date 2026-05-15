# Defense AI Theme - Prompts

These are the LLM prompts the defense-ai runtime uses to drive the
sources -> claims -> decision-packets pipeline. Adapted from the
canonical peptides reference; ASCII-clean (em-dash -> `--`) and
sector-specialized (defense vocabulary, defense category half-lives).

When adapting these for another contract-driven sector, keep the JSONL
contract on extract.md and the section order on packet.md. Swap only
entity slugs and topic vocabulary.

---

## extract.md

```
You are extracting atomic factual claims from a source document about the defense-AI sector.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, contract IDs, program names, or regulatory references.
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

HALF-LIFE GUIDANCE (defense-AI):
- regulatory (DoD policy, ITAR, BIS list update, NDAA passage): 60
- corporate (contract awards, fundraises, IPOs, partnerships, exec moves): 60
- supply (chips, rare earths, propellant): 180
- manufacturing (program-of-record manufacturing, fab capacity): 365
- market (NDAA / RDT&E line items, hyperscaler defense PPAs): 365
- research (DARPA programs, JADC2 / CJADC2 milestones, RPP awards): 365

CONFIDENCE GUIDANCE:
- 0.9+: primary source (DoD contract announcement, DARPA BAA, SEC filing, company IR)
- 0.7-0.9: reputable secondary (Reuters, Bloomberg, Defense News, Breaking Defense)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "palantir", "leidos", "aerovironment", "kratos", "anduril", "shield_ai",
  "skydio", "saildrone", "saronic", "vannevar_labs", "booz_allen", "caci",
  "saic", "hii", "axon", "lockheed_martin", "northrop_grumman", "raytheon",
  "general_dynamics", "rocket_lab", "dod", "darpa", "bis", "doe"

TOPIC NAMES (lowercase). Examples for defense-AI:
  "replicator", "cca", "jadc2", "cjadc2", "lattice", "vbat", "switchblade",
  "valkyrie", "blue_uas", "ota", "rdt_e", "ndaa", "itar", "aukus",
  "loitering_munition", "usv", "uas", "autonomous_weapon", "decision_advantage"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the defense-AI sector.

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
the layer (software / data spine / autonomous platform / services integration / prime
manufacturer / fuel-cycle analog). If the answer is "nobody captures durable margin," say that.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Visible in a DoD contract feed, NDAA tracker, or public filing within 60 days
- Concrete enough to wire up a monitor for
- Independent of the others

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Pull last 4 quarters of PLTR USG segment revenue + IL5 / IL6 contract wins; build a delta table" -- GOOD
- "Set monitor for Anduril fundraise + Replicator tranche announcements; alert on either" -- GOOD
- "Read latest NDAA conference report Title II RDT&E section, tag autonomy line items" -- GOOD
- "Research the defense industry" -- BAD, too vague

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no recent DoD acquisition policy claims in corpus"), list them. Skip if sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the defense-AI corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "DoD cancelled Replicator tranche 3 on 2026-09-15" SUPERSEDES
  OLD: "Replicator tranche 3 awarded to AVAV / KTOS / Anduril 2025-11-12" (state change)
- NEW: "Anduril closed Series F at $14B post-money on 2026-08-22" SUPERSEDES
  OLD: "Anduril last priced at $8.5B post-money 2024-08-08" (updated metric)
- NEW: "BIS removed advanced AI inference chips from EAR Section 744 list 2026-12-01" SUPERSEDES
  OLD: "BIS added advanced AI inference chips to Section 744 list 2024-09-30" (state change)

SUPERSEDENCE DOES NOT EXIST for:
- Related but independent contract awards on the same program
- Claims about different fiscal years that are both still true
- Claims where new adds nuance but does not contradict

NEW CLAIMS (just extracted):
{new_claims}

EXISTING ACTIVE CLAIMS (same category, within 365 days, superseded_by IS NULL):
{existing_claims}

OUTPUT: JSONL, one object per supersedence found. No preamble, no postamble, no fences.

{"new_claim_id": 123, "supersedes_id": 87, "reason": "short reason"}

If no supersedences found, output absolutely nothing.
```
