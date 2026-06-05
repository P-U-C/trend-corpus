# Biomechanics Theme - Prompts

These are the LLM prompts the biomechanics runtime uses to drive the
sources -> claims -> decision-packets pipeline. They mirror the peptides /
robotics reference pattern while using human-movement, orthopedics, exoskeleton,
prosthetics, and musculoskeletal-digital-health vocabulary.

Three roles:

- **extract.md** -- run after ingest; turns one source's `raw_text` into a set
  of atomic claims (JSONL).
- **packet.md** -- run on demand; turns the active-claims set plus a question
  into a Decision Packet (markdown).
- **validate.md** -- run after extract; detects when a newly-extracted claim
  supersedes an existing claim, so the `superseded_by` pointer can be set.

The runtime parser reads the generic `topics` array (NOT a `<theme>_topics`
field) and the required fields `claim`, `category`, `date_of_evidence`; keep
those exact keys.

---

## extract.md

```
You are extracting atomic factual claims from a source document about the biomechanics industry -- the engineering and quantification of human movement: robot-assisted orthopedic surgery and joint reconstruction, powered medical and industrial exoskeletons / exosuits, prosthetics and bionics, rehabilitation robotics, musculoskeletal (MSK) digital health, and wearable motion sensing.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, named entities, device/product models, FDA/CE clearances, procedure or installed-base counts, reimbursement coverage, deployment counts, funding/IPO terms, or revenue/guidance metrics.
- If the source has no extractable claims (navigation page, error page, pure marketing), output nothing.

OUTPUT FORMAT:
One JSON object per line (JSONL). No preamble, no postamble, no markdown code fences.
Each JSON object must have exactly these fields:

{
  "claim": "single-sentence factual assertion, self-contained",
  "category": "regulatory | manufacturing | market | supply | corporate | research",
  "entities": ["lowercase-slug", ...],
  "topics": ["lowercase-name", ...],
  "date_of_evidence": "YYYY-MM-DD",
  "half_life_days": <int>,
  "confidence": <float 0.0-1.0>
}

HALF-LIFE GUIDANCE (how long before re-verification needed):
- regulatory posture, FDA 510(k)/PMA clearances, CE Mark, reimbursement/CMS coverage decisions, ISO/IEC device standards: 90
- corporate (fundraises, partnerships, IPOs, acquisitions, exec changes): 60
- implant/device manufacturing capacity, 3D-printing capacity, surgical-robot production: 365
- market size, installed base, procedure counts, deployment counts, payer membership: 365
- actuators, harmonic drives, motors, force/torque sensors, batteries, implant materials: 180
- research benchmarks, gait/locomotion stability, clinical outcome, motion-tracking accuracy: 365

CONFIDENCE GUIDANCE:
- 0.9+: primary source (SEC filing, FDA database, company IR, court docket)
- 0.7-0.9: reputable secondary (Reuters, WSJ, Bloomberg, MedTech Dive, Fierce Biotech, The Robot Report, MassDevice)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "stryker", "zimmer_biomet", "globus_medical", "myomo", "ekso_bionics", "lifeward", "materialise", "garmin", "hinge_health", "ottobock", "wandercraft", "sword_health", "german_bionic", "intuitive", "fda", "cms"

TOPICS: lowercase. Examples:
  "robotic_orthopedics", "joint_reconstruction", "surgical_robotics", "spine_surgery", "exoskeleton", "exosuit", "industrial_exosuit", "prosthetics", "bionics", "rehabilitation_robotics", "msk_digital_health", "motion_tracking", "gait_analysis", "wearable", "myoelectric_orthosis", "reimbursement", "3d_printed_implant"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the biomechanics industry.

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
the layer (robotic-ortho installed base / joint implant / exoskeleton hardware / prosthetics & bionics / MSK digital-health software / wearable). If the answer is
"nobody captures durable margin," say that.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Something visible in a news feed or public filing within 30 days
- Concrete enough to wire up a monitor for
- Independent of the others (not three flavors of the same signal)

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Build a robotic-ortho installed-base monitor tracking Mako, ROSA, and ExcelsiusGPS procedure counts and next-gen clearances" -- GOOD
- "Extract reimbursement-coverage and revenue-vs-guidance claims from MYO, EKSO, and LFWD quarterly materials" -- GOOD
- "Track Hinge Health post-IPO membership/margin trajectory and Sword Health valuation marks" -- GOOD
- "Research biomechanics companies" -- BAD, too vague
- "Consider investing in exoskeletons" -- BAD, not actionable

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no primary-source reimbursement-coverage claims in corpus"), list them.
Skip this section if evidence is sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the biomechanics corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "FDA cleared ROSA Knee with OptimiZe on 2025-11-14" SUPERSEDES
  OLD: "Zimmer Biomet's next-gen ROSA Knee is pending FDA clearance" (state update)
- NEW: "Myomo guided FY2025 revenue to $40-42M" SUPERSEDES
  OLD: "Myomo guided FY2025 revenue to $50-53M" (updated guidance for same entity)
- NEW: "Hinge Health reported Q2 2025 revenue of $139.1M" SUPERSEDES
  OLD: "Hinge Health reported Q1 2025 revenue of $124M" (updated metric, same entity)

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
