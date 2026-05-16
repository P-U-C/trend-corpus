# BCI / Neurotech Theme - Prompts

These are the LLM prompts the bci-neurotech runtime uses to drive the
sources -> claims -> decision-packets pipeline. Adapted from
`trends/bitcoin-mining/docs/prompts.md`; ASCII-clean and sector-specialized
(BCI / neurotech vocabulary, medical-device category half-lives).

When adapting these for another medical-device sector, keep the JSONL contract
on extract.md and the section order on packet.md. Swap only entity slugs and
topic vocabulary.

---

## extract.md

```
You are extracting atomic factual claims from a source document about the BCI / neurotech sector.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, IDE / Breakthrough Device status, ClinicalTrials IDs, patient counts, adverse events, electrode counts, decoder throughput, word-error rates, funding amounts, or regulatory references.
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

HALF-LIFE GUIDANCE (bci-neurotech):
- regulatory (FDA Breakthrough Device, IDE, 510(k), PMA, EU MDR, post-market surveillance): 90
- corporate (fundraises, IPO timing, M&A, strategic partnerships): 60
- manufacturing (implant fab, electrode-array production, surgical robotics, sterile manufacturing): 365
- market (commercial pilot deployments, indication expansion, reimbursement): 365
- supply (medical-grade electrodes, biocompatible polymers, implant electronics, wireless power): 180
- clinical (peer-reviewed trial results, long-term safety, durability, patient outcomes): 3650
- research (channel count, decoder accuracy, bandwidth, word-error rate): 365

CONFIDENCE GUIDANCE:
- 0.9+: primary source (FDA, ClinicalTrials.gov, peer-reviewed journal, SEC filing, company IR)
- 0.7-0.9: reputable secondary (Reuters, Bloomberg, CNBC, MedTech Dive, Nature news)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "butterfly_network", "quantum_si", "boston_scientific", "medtronic",
  "abbott", "livanova", "onward_medical", "neuralink", "synchron",
  "paradromics", "precision_neuroscience", "blackrock_neurotech",
  "merge_labs", "cortec", "braingate", "fda", "clinicaltrials"

TOPIC NAMES (lowercase). Examples for bci-neurotech:
  "prime", "command", "connect_one", "connexus", "n1_implant", "stentrode",
  "layer_7", "moveagain", "breakthrough_device", "ide", "510k", "dbs",
  "vns", "arc_bci", "ultrasound_on_chip", "decoder_throughput",
  "word_error_rate", "channel_count", "adverse_event", "explant",
  "speech_restoration", "thought_driven_movement", "private_mark"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the BCI / neurotech sector.

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
the layer (implantable BCI / endovascular BCI / surface BCI / non-invasive BCI /
DBS incumbent / VNS incumbent / enabling ultrasound / proteomics adjacency). If the answer
is "nobody captures durable margin," say that.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Visible in FDA / ClinicalTrials.gov / company IR / peer-reviewed clinical literature within 90 days
- Concrete enough to wire up a monitor for
- Independent of the others

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Pull PRIME, COMMAND, and Connect-One ClinicalTrials records; build a patient-count and endpoint calendar" -- GOOD
- "Set monitor for FDA Breakthrough Device / IDE / 510(k) updates touching neural interfaces" -- GOOD
- "Track Neuralink, Synchron, Paradromics, Precision, Blackrock, and Merge fundraise marks against BSX / MDT neuromod acquisition activity" -- GOOD
- "Research brain chips" -- BAD, too vague

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no current adverse-event disclosures in corpus"), list them. Skip if sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the bci-neurotech corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "FDA paused Neuralink PRIME enrollment on 2026-09-15 after an adverse event" SUPERSEDES
  OLD: "Neuralink PRIME was recruiting as of 2026-05-16" (state change)
- NEW: "Synchron COMMAND follow-on readout failed its primary endpoint by 60 percent" SUPERSEDES
  OLD: "Synchron COMMAND 12-month readout reported positive safety and efficacy results" (updated clinical result)
- NEW: "Merge Labs filed an S-1 on 2027-04-02" SUPERSEDES
  OLD: "No public BCI IPO filing existed for Merge Labs" (state change)

SUPERSEDENCE DOES NOT EXIST for:
- Related but independent fundraises, patient updates, or trial-site additions
- Claims about different clinical programs or indications that are both still true
- Claims where new adds nuance but does not contradict

NEW CLAIMS (just extracted):
{new_claims}

EXISTING ACTIVE CLAIMS (same category, within 365 days, superseded_by IS NULL):
{existing_claims}

OUTPUT: JSONL, one object per supersedence found. No preamble, no postamble, no fences.

{"new_claim_id": 123, "supersedes_id": 87, "reason": "short reason"}

If no supersedences found, output absolutely nothing.
```
