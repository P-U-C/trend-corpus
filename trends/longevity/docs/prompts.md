# Longevity Theme - Prompts

These are the LLM prompts the longevity runtime uses to drive the
sources -> claims -> decision-packets pipeline. Adapted from
`trends/synthetic-biology/docs/prompts.md`; ASCII-clean and sector-
specialized (aging-biology vocabulary, FDA CBER and clinical
category half-lives).

When adapting these for another aging-adjacent sector, keep the JSONL
contract on extract.md and the section order on packet.md. Swap only
entity slugs and topic vocabulary.

---

## extract.md

```
You are extracting atomic factual claims from a source document about the longevity / aging-biology therapeutics sector.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, patient counts, GrimAge / PhenoAge deltas, NLRP3 / mTOR / APJ binding metrics, AAV vector dose, Yamanaka factor combinations, IND clearance dates, FDA RMAT designations, fundraise marks, contract values, or filing references.
- If the source has no extractable claims (navigation page, error page, pure marketing), output nothing.

OUTPUT FORMAT:
One JSON object per line (JSONL). No preamble, no postamble, no markdown code fences.
Each JSON object must have exactly these fields:

{
  "claim": "single-sentence factual assertion, self-contained",
  "category": "regulatory | corporate | manufacturing | market | supply | clinical | research",
  "entities": ["lowercase-slug", ...],
  "topics": ["lowercase-name", ...],
  "date_of_evidence": "YYYY-MM-DD",
  "half_life_days": <int>,
  "confidence": <float 0.0-1.0>
}

HALF-LIFE GUIDANCE (longevity):
- regulatory (FDA RMAT / IND for partial reprogramming, ICH aging-endpoint guidance, FDA AERS): 90
- corporate (partnership end events like AbbVie-Calico, fundraises, IPOs, M&A): 60
- manufacturing (AAV vector capacity, cell-therapy GMP for reprogramming, small-molecule CMO): 365
- market (commercial revenue once anything ships; veterinary Loyal as only current commercial signal): 365
- supply (mRNA / LNP reagents, viral vectors, cellular-reprogramming TF reagents): 180
- clinical (peer-reviewed trial readouts -- the longest half-life category; structural): 3650
- research (aging biomarkers, reprogramming techniques, senolytic chemistry): 365

CONFIDENCE GUIDANCE:
- 0.9+: primary source (SEC filing, company IR, FDA CBER docket, peer-reviewed journal, ClinicalTrials.gov)
- 0.7-0.9: reputable secondary (Reuters, Bloomberg, BioPharma Dive, Fierce Biotech, Longevity.Technology, BioSpace)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "bioage", "unity_bio", "abbvie", "alphabet", "lilly_longevity",
  "novo_nordisk", "insilico", "altos", "calico", "loyal", "retro",
  "newlimit", "life_bio", "rejuvenate_bio", "fda_cber"

TOPIC NAMES (lowercase). Examples for longevity:
  "bge_102", "azelaprag", "apj_agonist", "nlrp3", "ubx1325",
  "fosigotifator", "abbv_cls_628", "calico_partnership_end",
  "partial_reprogramming", "yamanaka_factors", "aav_delivery",
  "hsc_reprogramming", "autophagy", "rapamycin", "mtor",
  "senolytic", "epigenetic_clock", "grimage", "phenoage",
  "fda_rmat", "fda_conditional_approval", "ind_clearance",
  "pearl_trial", "newlimit_series_b", "altos_clinical_2026",
  "loyal_canine_approval", "insilico_hkex_ipo", "ai_engineered_protein"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the longevity / aging-biology therapeutics sector.

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
the layer (near-pure-play public clinical-stage developer / distressed precedent /
large-cap pharma optionality / HKEX-listed AI-bio / private reprogramming keystone /
veterinary commercial datapoint). If the answer is "nobody captures durable margin,"
say that. Be honest about the thin public surface.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Visible in a public company IR page, FDA CBER docket, ClinicalTrials.gov,
  peer-reviewed journal, or large-cap pharma earnings commentary within 90 days
- Concrete enough to wire up a monitor for
- Independent of the others

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Pull last 4 quarters of BIOA BGE-102 Phase 1 SAD safety data, APJ IND submission timeline, and cash runway; build a delta table" -- GOOD
- "Set monitor for FDA CBER cellular and gene therapy product page for clinical hold or RMAT announcements touching partial-reprogramming INDs" -- GOOGD
- "Read NewLimit, Altos, Retro Biosciences, Loyal news pages for first-in-human dosing, fundraise marks, or commercial launch updates; tag affected entities" -- GOOD
- "Research longevity" -- BAD, too vague

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no current GrimAge or PhenoAge delta readouts from intervention trials in
corpus"), list them. Skip if sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the longevity corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "BioAge BGE-102 failed Phase 2 primary endpoint on 2026-09-15" SUPERSEDES
  OLD: "BGE-102 reported positive interim Phase 1 SAD data December 2025" (state change in the program-status field)
- NEW: "Alphabet announced wind-down of Calico Life Sciences on 2026-10-01 transferring assets to a third party" SUPERSEDES
  OLD: "Post-AbbVie exit, Calico must source new partners or fund standalone" (resolution of the unresolved question)
- NEW: "FDA placed clinical hold on Altos Labs first-in-human partial-reprogramming trial on 2026-11-01" SUPERSEDES
  OLD: "Altos Labs initiated human clinical trials in neurodegenerative and immune-related aging disorders by 2026" (regulatory state change)

SUPERSEDENCE DOES NOT EXIST for:
- Related but independent program updates from different developers
- Claims about different chemistries or modalities (senolytic vs. partial reprogramming vs. autophagy enhancement) that remain independently true
- Claims where new adds nuance but does not contradict

NEW CLAIMS (just extracted):
{new_claims}

EXISTING ACTIVE CLAIMS (same category, within 365 days, superseded_by IS NULL):
{existing_claims}

OUTPUT: JSONL, one object per supersedence found. No preamble, no postamble, no fences.

{"new_claim_id": 123, "supersedes_id": 87, "reason": "short reason"}

If no supersedences found, output absolutely nothing.
```
