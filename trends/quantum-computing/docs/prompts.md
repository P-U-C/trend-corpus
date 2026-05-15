# Quantum Computing Theme - Prompts

These are the LLM prompts a quantum-computing runtime can use to drive the
sources -> claims -> decision-packets pipeline. They mirror the peptides
reference pattern while using quantum-computing vocabulary.

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
You are extracting atomic factual claims from a source document about the quantum-computing industry.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, named entities, system names, qubit counts, fidelity metrics, regulatory references, or customer categories.
- If the source has no extractable claims (navigation page, error page, pure marketing), output nothing.

OUTPUT FORMAT:
One JSON object per line (JSONL). No preamble, no postamble, no markdown code fences.
Each JSON object must have exactly these fields:

{
  "claim": "single-sentence factual assertion, self-contained",
  "category": "regulatory | manufacturing | market | research | pricing | corporate | supply",
  "entities": ["lowercase-slug", ...],
  "quantum_layers": ["lowercase-name", ...],
  "date_of_evidence": "YYYY-MM-DD",
  "half_life_days": <int>,
  "confidence": <float 0.0-1.0>
}

HALF-LIFE GUIDANCE (how long before re-verification needed):
- regulatory posture, BIS controls, NIST timelines, federal guidance: 90
- quantum cloud pricing / quantum-credit pricing: 365
- corporate (capital raises, partnerships, IPOs, acquisitions, exec changes): 60
- cryogenic capacity, helium-3 supply, control electronics, supplier lead times: 365
- market size, customer pilots, hyperscaler quantum-credit usage: 365
- research milestones, peer-reviewed gate fidelity, qubit count, logical qubit, error correction: 180

CONFIDENCE GUIDANCE:
- 0.9+: primary source (SEC filing, BIS announcement, NIST page, DOE page, company IR, court docket)
- 0.7-0.9: reputable secondary (Reuters, WSJ, Bloomberg, Nature, IEEE Spectrum, MIT Technology Review)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "ionq", "d_wave", "rigetti", "arqit", "quantum_computing_inc", "ibm", "alphabet", "microsoft", "psiquantum", "pasqal", "iqm", "bis", "nist", "doe", "bluefors", "oxford_instruments"

QUANTUM LAYERS: lowercase. Examples:
  "trapped_ion", "superconducting", "annealing", "photonic", "neutral_atom", "topological", "cryogenics", "control_electronics", "quantum_cloud", "pqc_migration", "error_correction", "logical_qubits"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the quantum-computing industry.

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
the layer (trapped ion / superconducting / annealing / photonic / neutral atom / cryogenics / quantum cloud / security migration). If the answer is
"nobody captures durable margin," say that.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Something visible in a news feed or public filing within 30 days
- Concrete enough to wire up a monitor for
- Independent of the others (not three flavors of the same signal)

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Build a BIS quantum-control monitor that alerts on new quantum hardware or cryogenic-system controls" -- GOOD
- "Extract the last four quarters of cash runway, bookings, and benchmark claims for IONQ, QBTS, and RGTI" -- GOOD
- "Read the latest Google, IBM, IonQ, and Rigetti benchmark papers and normalize two-qubit fidelity claims" -- GOOD
- "Research quantum computing companies" -- BAD, too vague
- "Consider investing in quantum" -- BAD, not actionable

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no primary-source cryogenic supplier lead-time claims in corpus"), list them.
Skip this section if evidence is sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the quantum-computing corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "IonQ reported USD 75M bookings for fiscal 2026" SUPERSEDES
  OLD: "IonQ reported USD 54M bookings for fiscal 2025" (updated metric for same entity)
- NEW: "Google published a logical-qubit milestone on 2026-06-22" SUPERSEDES
  OLD: "Google's latest public logical-qubit milestone was Willow in 2024" (direct state update)
- NEW: "BIS removed a control on a class of quantum computers in 2026" SUPERSEDES
  OLD: "BIS controls that class of quantum computers" (regulatory state change)

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
