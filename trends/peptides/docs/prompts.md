# Peptides Theme - Prompts

These are the LLM prompts the peptides runtime uses to drive the
sources -> claims -> decision-packets pipeline. They are published as the
canonical reference for spinning up the same pattern in a new sector.

Three roles:

- **extract.md** -- run after ingest; turns one source's `raw_text` into a set
  of atomic claims (JSONL).
- **packet.md** -- run on demand; turns the active-claims set plus a question
  into a Decision Packet (markdown).
- **validate.md** -- run after extract; detects when a newly-extracted claim
  supersedes an existing claim, so the `superseded_by` pointer can be set.

Only ASCII conversion was applied to the originals (em-dash -> `--`). The rest
is verbatim from the live runtime.

When adapting to a new sector:

1. Keep the JSONL contract for `extract` (the rest of the pipeline depends on it).
2. Keep the section order in `packet` (Verdict, Why now, What the evidence
   actually says, Who captures the margin, Invalidation triggers, Next actions,
   Confidence, Evidence gaps). Operators learn to scan packets in that order;
   reordering breaks the reading habit.
3. Swap the entity-slug and peptide-name conventions for the sector's
   equivalents (e.g. ticker slugs, drug names, materials, geographies).
4. Re-tune `half_life_days` only if the sector has structurally different
   freshness dynamics. The peptide defaults
   (regulatory=90, pricing=30, corporate=60, manufacturing=180, market=365,
   clinical=3650) are a workable starting point for most industries.

---

## extract.md

```
You are extracting atomic factual claims from a source document about the peptide industry.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, named entities, or regulatory references.
- If the source has no extractable claims (navigation page, error page, pure marketing), output nothing.

OUTPUT FORMAT:
One JSON object per line (JSONL). No preamble, no postamble, no markdown code fences.
Each JSON object must have exactly these fields:

{
  "claim": "single-sentence factual assertion, self-contained",
  "category": "regulatory | manufacturing | market | clinical | pricing | corporate",
  "entities": ["lowercase-slug", ...],
  "peptides": ["lowercase-name", ...],
  "date_of_evidence": "YYYY-MM-DD",
  "half_life_days": <int>,
  "confidence": <float 0.0-1.0>
}

HALF-LIFE GUIDANCE (how long before re-verification needed):
- pricing: 30
- regulatory posture, enforcement action, warning letter: 90
- corporate (partnerships, lawsuits, exec changes): 60
- market size / commercial volume: 365
- manufacturing capacity / capex: 180
- clinical trial result / pharmacology: 3650 (effectively evergreen)

CONFIDENCE GUIDANCE:
- 0.9+: primary source (SEC filing, FDA announcement, company IR, court docket)
- 0.7-0.9: reputable secondary (Reuters, WSJ, Bloomberg, STAT, Endpoints, FiercePharma)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "lilly", "novo", "bachem", "polypeptide", "hims", "ro", "empower", "fda", "health_canada"

PEPTIDE NAMES: lowercase. Examples:
  "semaglutide", "tirzepatide", "retatrutide", "bpc-157", "tb-500", "pt-141", "cjc-1295"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the peptide industry.

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
the layer (API / compounding / telehealth / enablement / diagnostics). If the answer is
"nobody captures durable margin," say that.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Something visible in a news feed or public filing within 30 days
- Concrete enough to wire up a monitor for
- Independent of the others (not three flavors of the same signal)

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Take a 1hr GLG call with a former Empower 503B ops lead on cost-to-serve" -- GOOD
- "Deploy $15K long position in BANB.SW as CDMO tracking" -- GOOD
- "Spend $500 on Google keyword research for 'canada generic semaglutide' cluster" -- GOOD
- "Research more about the regulatory landscape" -- BAD, too vague
- "Consider investing in peptide companies" -- BAD, not actionable

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no primary-source Canadian Health Canada guidance claims in corpus"), list them.
Skip this section if evidence is sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the peptide corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "Novo terminated Hims partnership 2026-06-22" SUPERSEDES
  OLD: "Novo partnered with Hims 2025-04-10" (direct state change)
- NEW: "FDA resolved semaglutide shortage 2025-02-21" SUPERSEDES
  OLD: "Semaglutide on FDA shortage list" (state change)
- NEW: "Bachem revenue reached CHF 1.1B in 2026" SUPERSEDES
  OLD: "Bachem revenue CHF 695M in 2025" (updated metric for same entity)

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
