# Solid-State Battery Theme - Prompts

These are the LLM prompts the solid-state-battery runtime uses to drive the
sources -> claims -> decision-packets pipeline. Adapted from
`trends/bitcoin-mining/docs/prompts.md`; ASCII-clean and sector-specialized
(solid-state vocabulary, manufacturing-clock category half-lives).

When adapting these for another battery-adjacent sector, keep the JSONL
contract on extract.md and the section order on packet.md. Swap only entity
slugs and topic vocabulary.

---

## extract.md

```
You are extracting atomic factual claims from a source document about the solid-state lithium battery sector.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, Wh/kg, Wh/L, mAh/g, cycle counts, charge rates (C-rate), mt/yr capacity, kt-scale tonnage, mm cell thickness, dollar contract values, IRA / DOE / NDAA regulatory thresholds, or filing references.
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

HALF-LIFE GUIDANCE (solid-state-battery):
- regulatory (DOE LPO awards, IRA 45X interpretive guidance, EU Battery Regulation passports, NHTSA / UNECE battery safety): 90
- corporate (OEM supply MOUs, JV announcements, fundraise marks, customer-billings disclosures): 60
- manufacturing (Eagle Line / Cobra throughput, pilot-line yield, A/B/C sample transitions): 365
- market (EV adoption curves, commercial pilot deployments, automotive design-in windows): 365
- supply (sulfide electrolyte / lithium-sulfide capacity, argyrodite tonnage, cathode / silicon-anode availability): 180
- research (energy density, cycle life, dendrite suppression, charge-rate benchmarks): 365

CONFIDENCE GUIDANCE:
- 0.9+: primary source (SEC filing, company IR, DOE / IRS / Treasury page, peer-reviewed journal)
- 0.7-0.9: reputable secondary (Reuters, Bloomberg, BloombergNEF, Electrek, Electrive, Charged EVs)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "quantumscape", "solid_power", "ses_ai", "toyota", "samsung_sdi",
  "sk_innovation", "lg_energy_solution", "idemitsu_kosan",
  "mitsui_mining_smelting", "factorial", "ampcera", "24m_technologies",
  "sila_nanotechnologies", "murata", "prologium", "ion_storage_systems",
  "powerco", "bmw", "mercedes_benz", "doe_lpo", "ira_45x", "nhtsa",
  "unece"

TOPIC NAMES (lowercase). Examples for solid-state-battery:
  "eagle_line", "cobra_separator", "qse_5", "sulfide_electrolyte",
  "argyrodite", "lithium_sulfide", "polymer_electrolyte", "oxide_llzo",
  "lithium_metal", "silicon_anode", "semi_solid", "b1_sample", "c_sample",
  "energy_density", "wh_kg", "cycle_life", "dendrite", "c_rate",
  "customer_billings", "joint_development", "ira_45x", "atvm",
  "title_17", "domestic_content", "powerco", "design_in_window"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the solid-state lithium battery sector.

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
the layer (pure-play cell developer / licensing platform / Asian incumbent cell maker /
sulfide-electrolyte supplier / silicon-anode supplier / OEM design-in / DOE-credit recipient).
If the answer is "nobody captures durable margin," say that.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Visible in a public company IR page, SEC filing, BloombergNEF / Electrive briefing, DOE LPO portfolio update, or peer-reviewed publication within 90 days
- Concrete enough to wire up a monitor for
- Independent of the others

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Pull last 4 quarters of QuantumScape customer billings, R-and-D opex, and PowerCo joint-development milestone disclosures; build a delta table" -- GOOD
- "Set monitor for Idemitsu Kosan or Mitsui Mining and Smelting sulfide-electrolyte capacity announcements above 500 mt/yr" -- GOOD
- "Read latest DOE LPO conditional commitments tied to U.S. cell or electrolyte manufacturing and tag exposed solid-state names" -- GOOD
- "Research batteries" -- BAD, too vague

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no current sulfide-electrolyte landed-cost-per-kg claims in corpus"), list them.
Skip if sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the solid-state-battery corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "QuantumScape Q2 2026 customer billings fell to $4M from $11M in Q1 2026" SUPERSEDES
  OLD: "QuantumScape recorded $11.0M of customer billings in Q1 2026" (state change at the quarterly metric level)
- NEW: "Toyota delayed its all-solid-state mass production target from 2027 to 2030 on 2026-09-01" SUPERSEDES
  OLD: "Toyota and Idemitsu target 2027-2028 mass production for sulfide solid-state cells" (updated schedule)
- NEW: "Idemitsu Kosan lithium-sulfide plant production capacity raised to 15 GWh-equivalent per year per October 2026 announcement" SUPERSEDES
  OLD: "Idemitsu Kosan lithium-sulfide facility targets 3 GWh-equivalent annual capacity and June 2027 completion" (updated capacity)

SUPERSEDENCE DOES NOT EXIST for:
- Related but independent program updates from different OEMs or cell makers
- Claims about different chemistries (sulfide vs. oxide vs. polymer) that remain independently true
- Claims where new adds nuance but does not contradict

NEW CLAIMS (just extracted):
{new_claims}

EXISTING ACTIVE CLAIMS (same category, within 365 days, superseded_by IS NULL):
{existing_claims}

OUTPUT: JSONL, one object per supersedence found. No preamble, no postamble, no fences.

{"new_claim_id": 123, "supersedes_id": 87, "reason": "short reason"}

If no supersedences found, output absolutely nothing.
```
