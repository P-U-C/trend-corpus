# Bitcoin Mining Theme - Prompts

These are the LLM prompts the bitcoin-mining runtime uses to drive the
sources -> claims -> decision-packets pipeline. Adapted from
`trends/space-satellite/docs/prompts.md`; ASCII-clean and sector-specialized
(Bitcoin-mining vocabulary, mining category half-lives).

When adapting these for another infrastructure sector, keep the JSONL contract
on extract.md and the section order on packet.md. Swap only entity slugs and
topic vocabulary.

---

## extract.md

```
You are extracting atomic factual claims from a source document about the Bitcoin-mining sector.

RULES:
- One claim per JSON object. Target 3-15 claims per source depending on density.
- Each claim is a single factual assertion, self-contained, verifiable from source text.
- Skip opinions, marketing language, speculative claims, and filler.
- Prefer claims with specific numbers, dates, EH/s, PH/s/day, MW, BTC mined, fleet efficiency, contract values, tariff language, regulatory thresholds, or filing references.
- If the source has no extractable claims (navigation page, error page, pure marketing), output nothing.

OUTPUT FORMAT:
One JSON object per line (JSONL). No preamble, no postamble, no markdown code fences.
Each JSON object must have exactly these fields:

{
  "claim": "single-sentence factual assertion, self-contained",
  "category": "regulatory | corporate | manufacturing | market | supply | pricing",
  "entities": ["lowercase-slug", ...],
  "topics": ["lowercase-name", ...],
  "date_of_evidence": "YYYY-MM-DD",
  "half_life_days": <int>,
  "confidence": <float 0.0-1.0>
}

HALF-LIFE GUIDANCE (bitcoin-mining):
- regulatory (SEC / CFTC / IRS guidance, state moratoria, ERCOT rules, EPA scrutiny): 60
- corporate (M&A, hosting agreements, capacity expansions, AI / HPC pivots, financings): 60
- manufacturing (ASIC release cycles, fleet upgrades, immersion buildouts): 180
- market (hashrate, network difficulty, miner economics, BTC price, treasury value): 90
- supply (ASIC concentration, chip fabrication, tariffs, delivery schedules): 180
- pricing (hashprice, power prices, electricity spreads): 30

CONFIDENCE GUIDANCE:
- 0.9+: primary source (SEC filing, company IR, ERCOT / PUC / IRS / state agency page)
- 0.7-0.9: reputable secondary (Reuters, Bloomberg, TheMinerMag, Hashrate Index, CoinDesk)
- 0.5-0.7: trade press, industry analyst, single-sourced report
- <0.5: do not emit; skip the claim

ENTITY SLUGS: use short lowercase names. Examples:
  "mara", "riot", "cleanspark", "hut8", "bit_digital", "hive",
  "terawulf", "iren", "bitfarms", "cipher_mining", "argo_blockchain",
  "core_scientific", "canaan", "bitmain", "microbt", "ercot", "texas_puc",
  "nysdec", "irs"

TOPIC NAMES (lowercase). Examples for bitcoin-mining:
  "hashprice", "network_difficulty", "halving", "block_subsidy", "transaction_fees",
  "btc_treasury", "energized_hashrate", "deployed_hashrate", "fleet_efficiency",
  "j_per_th", "cash_cost_per_coin", "s21", "s21xp", "whatsminer", "avalon",
  "asic_tariffs", "large_flexible_load", "curtailment", "ercot", "sb6",
  "ai_hpc", "high_density_colocation", "power_pipeline", "hyperscaler_lease"

SOURCE URL: {url}
SOURCE DATE (if known): {source_date}

SOURCE TEXT:
{text}
```

---

## packet.md

```
You are producing a Decision Packet on a specific question about the bitcoin-mining sector.

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
the layer (pure-play miner / power-first miner / AI-HPC colocation / ASIC supplier /
pool operator / power market / BTC treasury). If the answer is "nobody captures durable margin,"
say that.

## Invalidation triggers
Exactly 3 specific, observable signals that would flip the verdict. Each must be:
- Visible in Hashrate Index, a public miner filing, an ERCOT / PUC docket, or company IR within 60 days
- Concrete enough to wire up a monitor for
- Independent of the others

## Next actions
Exactly 3 concrete actions executable this week. Each must be specific enough to do today:
- "Pull last 4 quarters of MARA / RIOT / CLSK energized hashrate, BTC mined, BTC treasury, and cash cost per coin; build a delta table" -- GOOD
- "Set monitor for Hashrate Index hashprice below $40/PH/day for 4 consecutive weeks" -- GOOD
- "Read latest Texas PUC large flexible load filings and tag miners with ERCOT interconnection exposure" -- GOOD
- "Research crypto miners" -- BAD, too vague

## Confidence
One sentence on how strong this evidence base is. One sentence on what would most
strengthen it. If the evidence base is weak (<20 relevant claims, or claims average
confidence <0.7), say so plainly and lower the verdict accordingly.

## Evidence gaps
Optional section. If there are 1-3 claim types you'd want but don't have (e.g.
"no current ASIC landed-cost claims in corpus"), list them. Skip if sufficient.
```

---

## validate.md

```
You are checking whether new claims supersede any existing claims in the bitcoin-mining corpus.

SUPERSEDENCE EXISTS when a new claim asserts a state of the world that directly
contradicts or updates an existing claim. Examples:
- NEW: "Hashprice stayed below $40/PH/day for 4 consecutive weeks through 2026-08-15" SUPERSEDES
  OLD: "Hashprice recovered above $45/PH/day in May 2026" (state change)
- NEW: "Texas PUC delayed SB 6 large-load interconnection standards until 2027" SUPERSEDES
  OLD: "Texas SB 6 large-load interconnection standards were scheduled for 2026 implementation" (updated schedule)
- NEW: "Bitmain S21 XP landed cost increased more than 50 percent after new tariffs on 2026-09-01" SUPERSEDES
  OLD: "S21 XP tariff risk was disclosed but had not yet changed landed fleet-upgrade cost" (updated metric)

SUPERSEDENCE DOES NOT EXIST for:
- Related but independent monthly production updates
- Claims about different miners, power markets, or fiscal quarters that are both still true
- Claims where new adds nuance but does not contradict

NEW CLAIMS (just extracted):
{new_claims}

EXISTING ACTIVE CLAIMS (same category, within 365 days, superseded_by IS NULL):
{existing_claims}

OUTPUT: JSONL, one object per supersedence found. No preamble, no postamble, no fences.

{"new_claim_id": 123, "supersedes_id": 87, "reason": "short reason"}

If no supersedences found, output absolutely nothing.
```
