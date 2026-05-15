# Nuclear / SMR Theme - Prompts

These are the LLM prompts a nuclear and SMR runtime can use to drive the
sources -> claims -> decision-packets pipeline. They mirror the peptides
reference pattern while using nuclear, fuel-cycle, and data-center power
vocabulary.

Three roles:

- **extract.md** -- run after ingest; turns one source's `raw_text` into a set
  of atomic claims (JSONL).
- **packet.md** -- run on demand; turns the active-claims set plus a question
  into a Decision Packet (markdown).
- **validate.md** -- run after extract; detects when a newly-extracted claim
  supersedes an existing claim, so the `superseded_by` pointer can be set.

When adapting this prompt to another non-peptide sector:

1. Keep the JSONL contract for `extract`; the rest of the pipeline depends on
   one JSON object per factual claim.
2. Keep the section order in `packet`: Verdict, Why now, What the evidence
   actually says, Who captures the margin, Invalidation triggers, Next actions,
   Confidence, Evidence gaps.
3. Swap sector entity examples, component examples, and half-life guidance.
4. Keep trade-relevant outputs framed as watchlist or research artifacts that
   require human review.

---

## extract.md

```
You are extracting atomic factual claims from a source document about the nuclear and SMR industry.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, named entities, license docket references, fuel-cycle quantities, PPA terms, capacity figures, or project milestones.
- If the source has no extractable claims (navigation page, error page, pure marketing), output nothing.

OUTPUT FORMAT:
One JSON object per line (JSONL). No preamble, no postamble, no markdown code fences.
Each JSON object must have exactly these fields:

{
  "claim": "single-sentence factual assertion, self-contained",
  "category": "regulatory | manufacturing | market | supply | pricing | corporate | research",
  "entities": ["lowercase-slug", ...],
  "nuclear_topics": ["lowercase-name", ...],
  "date_of_evidence": "YYYY-MM-DD",
  "half_life_days": <int>,
  "confidence": <float 0.0-1.0>
}

HALF-LIFE GUIDANCE (how long before re-verification needed):
- regulatory posture, NRC licensing action, DOE policy, enrichment export controls: 90
- uranium spot price, long-term contract price, SWU pricing: 90
- corporate (PPA announcements, capital raises, M&A, partnerships, exec changes): 60
- reactor module fabrication, fuel-fab capacity, utility capex: 365
- HALEU supply, conversion, enrichment capacity, uranium supply: 180
- market size, hyperscaler PPA flow, utility capex, ITC tax-credit applications: 365
- license-application milestones, NRC reviews, project technical readiness: 365

CONFIDENCE GUIDANCE:
- 0.9+: primary source (SEC filing, NRC docket, DOE announcement, company IR, court docket)
- 0.7-0.9: reputable secondary (Reuters, WSJ, Bloomberg, World Nuclear News, Power Magazine, ANS)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "bwxt", "oklo", "nuscale", "ge_vernova", "constellation", "cameco", "centrus", "vistra", "nrg", "uranium_energy", "nexgen_energy", "nrc", "doe", "nei", "nea", "x_energy", "kairos_power", "terrapower"

NUCLEAR TOPICS: lowercase. Examples:
  "haleu", "smr", "ppa", "conversion", "enrichment", "fuel_fab", "advanced_reactor", "lwsmr", "nrc_part_53", "part_52", "uranium", "reactor_restart", "data_center_power"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the nuclear and SMR industry.

THE USER is a sophisticated crypto-native investor/builder with zero appetite for hedging,
generic disclaimers, or "on one hand, on the other" waffling. They want a ranked,
opinionated answer backed by the evidence below, with specific actions they can take today.
They are the filter on your output -- your job is to produce packets fast enough that they
can say yes or no quickly, not to produce the definitive answer.

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
A tight synthesis of the relevant claims (not a summary of every claim -- only those
that bear on the question). Cite claim IDs inline like [C-42, C-87]. Flag contradictions
explicitly. Explicitly call out any load-bearing claim with confidence <0.6.

## Who captures the margin
2-3 sentences on where value accrues given this specific question. Be specific about
the layer (uranium mining / conversion / enrichment / HALEU / reactor developer / nuclear utility / data-center PPA / reactor services). If the answer is
"nobody captures durable margin," say that.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Something visible in a news feed or public filing within 30 days
- Concrete enough to wire up a monitor for
- Independent of the others (not three flavors of the same signal)

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Build an NRC docket monitor for Oklo, NuScale, GE Vernova Hitachi, TerraPower, Kairos, and X-energy projects" -- GOOD
- "Extract HALEU, SWU, uranium, and DOE task-order claims from the latest Centrus and Cameco filings" -- GOOD
- "Track all hyperscaler nuclear PPAs by counterparty, MW, term length, start year, and project status" -- GOOD
- "Research nuclear companies" -- BAD, too vague
- "Consider investing in nuclear" -- BAD, not actionable

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no primary-source HALEU allocation claims in corpus"), list them.
Skip this section if evidence is sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the nuclear and SMR corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "NRC accepted Oklo's combined license application on 2026-06-22" SUPERSEDES
  OLD: "Oklo has not yet submitted a combined license application" (direct state update)
- NEW: "DOE awarded a HALEU production task order to Centrus in 2026" SUPERSEDES
  OLD: "Centrus is awaiting a DOE HALEU production task order" (state change)
- NEW: "Constellation and Microsoft increased the Crane PPA from 835 MW to 1,000 MW" SUPERSEDES
  OLD: "The Crane PPA covers 835 MW" (updated metric for same agreement)

SUPERSEDENCE DOES NOT EXIST for:
- Related but independent facts about the same entity
- Claims about different time periods that are both still true
- Claims where new adds nuance but does not contradict

NEW CLAIMS (just extracted):
{new_claims}

EXISTING ACTIVE CLAIMS (same category, within 365 days, superseded_by IS NULL):
{existing_claims}

OUTPUT: JSONL, one object per supersedence found. No preamble, no postamble, no fences.

{"new_claim_id": 123, "supersedes_id": 87, "reason": "short reason"}

If no supersedences found, output absolutely nothing.
```
