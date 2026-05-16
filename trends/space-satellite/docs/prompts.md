# Space / Satellite Theme - Prompts

These are the LLM prompts the space-satellite runtime uses to drive the
sources -> claims -> decision-packets pipeline. Adapted from
`trends/defense-ai/docs/prompts.md`; ASCII-clean and sector-specialized
(space vocabulary, space category half-lives).

When adapting these for another contract-driven sector, keep the JSONL
contract on extract.md and the section order on packet.md. Swap only
entity slugs and topic vocabulary.

---

## extract.md

```
You are extracting atomic factual claims from a source document about the space-satellite sector.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, contract IDs, license grants, satellite counts, launch cadence, program names, or regulatory references.
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

HALF-LIFE GUIDANCE (space-satellite):
- regulatory (FCC spectrum, FAA launch licensing, ITU coordination): 90
- corporate (contract awards, fundraises, IPOs, partnerships, government award notices): 60
- supply (Ka / Ku / V-band payloads, phased arrays, RF ASICs, optical terminals, solar arrays): 180
- manufacturing (sat-bus production, launch cadence, ground-network deployment): 365
- market (broadband ARPU, government imagery contracts, defense launches): 365
- research (constellation milestones, optical inter-sat links, lunar mission learnings): 365

CONFIDENCE GUIDANCE:
- 0.9+: primary source (FCC / NASA / NRO / DOD order, SEC filing, company IR)
- 0.7-0.9: reputable secondary (Reuters, Bloomberg, SpaceNews, Via Satellite)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "rocket_lab", "ast_spacemobile", "planet_labs", "intuitive_machines",
  "iridium", "viasat", "globalstar", "kratos", "l3harris",
  "lockheed_martin", "northrop_grumman", "echostar", "spacex",
  "firefly_aerospace", "maxar", "fcc", "faa", "nasa", "nro", "sda", "dod"

TOPIC NAMES (lowercase). Examples for space-satellite:
  "scs", "direct_to_device", "d2d", "bluebird", "starlink", "starship",
  "falcon_9", "neutron", "electron", "clps", "eocl", "pwsa", "sda_tranche",
  "v_band", "e_band", "ka_band", "ku_band", "rf_asic", "phased_array",
  "optical_inter_sat_link", "earth_observation", "lunar_transport"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the space-satellite sector.

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
the layer (launch provider / satellite bus / spectrum holder / D2D operator / imagery data layer /
ground system / prime integrator / lunar transport). If the answer is "nobody captures durable margin,"
say that.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Visible in an FCC docket, NASA / NRO / SDA / DOD award feed, launch manifest, or public filing within 90 days
- Concrete enough to wire up a monitor for
- Independent of the others

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Pull last 4 quarters of ASTS gateway / MNO revenue and BlueBird launch disclosures; build a cadence table" -- GOOD
- "Set monitor for FCC SCS grants and AST / Starlink / Iridium D2D service activations" -- GOOD
- "Read latest NRO EOCL / CSO award notices; tag Planet and Maxar-related award expansions" -- GOOD
- "Research the space industry" -- BAD, too vague

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no recent FCC SCS grants in corpus"), list them. Skip if sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the space-satellite corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "FCC denied AST's 248-satellite SCS authorization on 2026-09-15" SUPERSEDES
  OLD: "FCC granted AST's 248-satellite SCS authorization on 2026-04-21" (state change)
- NEW: "Rocket Lab moved Neutron first launch target from Q4 2026 to mid-2027" SUPERSEDES
  OLD: "Rocket Lab targeted Neutron first launch for Q4 2026" (updated schedule)
- NEW: "Planet lost the NRO EOCL option renewal for FY2027" SUPERSEDES
  OLD: "Planet's EOCL renewal extended baseline PlanetScope monitoring through FY2026" (state change)

SUPERSEDENCE DOES NOT EXIST for:
- Related but independent launch contracts or satellite launches
- Claims about different task orders, dockets, or fiscal years that are both still true
- Claims where new adds nuance but does not contradict

NEW CLAIMS (just extracted):
{new_claims}

EXISTING ACTIVE CLAIMS (same category, within 365 days, superseded_by IS NULL):
{existing_claims}

OUTPUT: JSONL, one object per supersedence found. No preamble, no postamble, no fences.

{"new_claim_id": 123, "supersedes_id": 87, "reason": "short reason"}

If no supersedences found, output absolutely nothing.
```
