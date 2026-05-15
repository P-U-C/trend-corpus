# Metalayer

## 1. Purpose

The metalayer is a typed decision service. It is not a chatbot, not an agent that improvises execution, and not a live trading system.

Its job is to consume structured inputs, apply documented routing and scoring rubrics, and emit structured outputs that humans and private runtimes can review. The metalayer reuses the peptides pattern at a cross-theme level: sources feed claims, claims feed theses, and theses feed decision packets with explicit invalidation conditions.

Inputs:

- Public `trend-corpus` theme objects.
- Private convergence artifacts.
- Private runtime state summaries.

Outputs:

- Cross-theme theses.
- Exposure maps.
- Convergence deltas.
- Watchlist rankings.
- Decision packets with deliberate execution state.
- Trade-relevant candidates gated for human review.

## 2. Inputs

### Public Trend-Corpus Themes

The metalayer reads this repo as a read-only corpus. Theme manifests, sources, claims, entities, events, theses, decision packets, and watchlists provide the public structure.

Public theme objects must pass `make validate` before registration. Public objects are evidence and routing inputs, not execution commands.

### Private Convergence Artifacts

Private convergence artifacts live outside this repo at:

```text
~/puc-trading/corpus/convergence-latest.json
```

The file must conform to `schemas/convergence.schema.json`. The M1 contract requires each score row to include at minimum:

- `ticker`
- `theme`
- `score`
- `tier`
- `status`

The artifact is read through a file seam. The public corpus does not import private scanner code or hold private credentials.

### Private Runtime State

Each theme runtime keeps its own private database and operational state. The metalayer reads aggregated views from those runtimes, not raw claim history.

Examples of acceptable aggregated views:

- Fresh-claim counts by category.
- Theme freshness windows.
- Claim confidence summaries.
- Watchlist drift summaries.
- Runtime health and last-update timestamps.

Raw private packets, personal trade context, broker configuration, and credential material are never inputs to the public corpus.

## 3. Outputs

### Cross-Theme Theses

Cross-theme theses connect evidence across sectors. Example:

```text
peptide manufacturing thesis + AI infra thesis -> shared CDMO automation supplier exposure
```

These theses should cite public theme claims and private aggregate summaries where applicable.

### Ticker And Entity Exposure Maps

Exposure maps identify where the same ticker, supplier, customer, technology, or regulator appears across themes.

The output is a typed map, not prose speculation. It should preserve source theme, supporting claim IDs, confidence, and freshness.

### Convergence Deltas

Convergence deltas compare current and prior convergence artifacts. The usual comparison window is week over week.

Tracked changes include:

- Score movement.
- Tier movement.
- Status movement.
- New entrants.
- Dropped tickers.
- Theme-level rank changes.

### Watchlist Rankings

Watchlist rankings combine public theme evidence, private aggregate freshness, convergence deltas, and operator-defined review priorities.

Rankings are review queues. They are not execution queues.

### Decision Packets

Decision packets must include:

- A specific question.
- A verdict.
- Supporting theses or claims.
- Non-empty invalidation conditions.
- A deliberately chosen `execution_state`.

Trade-relevant packets in public outputs must use `human_review_required`.

### Human-Review-Required Candidates

The metalayer may emit candidate opportunities for human review. These candidates must state why they are being surfaced, what evidence supports them, and what would invalidate them.

They must never bypass the human-review gate.

## 4. State Machine

```text
+---------------+       +---------------------+       +-----------------------+
| research_only | ----> | watchlist_candidate | ----> | human_review_required |
+---------------+       +---------------------+       +-----------------------+
        ^                         ^                              |
        |                         |                              v
        +-------------------------+                  +-------------------------------+
                                                   | approved_for_private_execution |
                                                   +-------------------------------+
```

Forward transitions require explicit promotion criteria:

- `research_only` to `watchlist_candidate`: enough source coverage and validated references exist to monitor the theme or entity.
- `watchlist_candidate` to `human_review_required`: evidence, convergence movement, or runtime state crosses a documented review threshold.
- `human_review_required` to private approval: a human reviews the packet, invalidation conditions, runtime state, and risk context.

`approved_for_private_execution` lives in private runtime only. The public corpus must not contain that state in actual corpus objects.

Backward transitions are always allowed. Any object can be demoted when evidence weakens, freshness expires, references fail, or a reviewer rejects the packet.

## 5. Decision-Routing Contract

The metalayer routes questions through a declarative scoring rubric over current claims and runtime summaries.

Routing inputs:

- Theme match: which theme IDs and aliases match the question.
- Entity match: which tickers, companies, suppliers, regulators, or technologies are referenced.
- Claim freshness: whether supporting claims are still inside their category half-life.
- Claim confidence: source quality and corroboration level.
- Thesis coverage: whether existing theses already combine the relevant claims.
- Convergence relevance: whether private convergence rows exist for the same theme or entity.
- Runtime health: whether private aggregate views are current.
- Human-review sensitivity: whether the question is trade-relevant.

Routing outputs:

- The best matching theme or set of themes.
- The thesis or thesis gap to surface.
- The decision packet to return or create as a candidate.
- The execution state required for the answer.

The contract is intentionally declarative. Implementations may change scoring weights, but they must preserve explainable inputs and typed outputs.

## 6. Agent-Spinup Workflow

When the operator wants a new sector, the metalayer supports a repeatable spinup flow.

1. Claude orchestrator and Codex research-mode independently enumerate candidate sources, claim categories, entities, and open questions.
2. Outputs are aggregated. A third agent or human reviewer reconciles disagreements, drops weak sources, and selects the first theme scope.
3. The new theme is committed by copying `trends/_template/` and filling `trend.yaml`.
4. A first batch of example claims is generated, usually 3 to 5 claims plus 1 thesis and 1 decision packet. `make validate` gates the commit.
5. The metalayer registers the new theme after validation passes and the reviewer accepts the theme scope.

Research-mode is the slow, expensive pass. It is for discovering the shape of the sector and high-quality upstream sources.

Live runtime extract is the fast pass. It refreshes known source streams, updates claims, and emits aggregate views for the metalayer.

## 7. Failure Modes

The metalayer must not:

- Emit `approved_for_private_execution` into public outputs.
- Emit a decision packet without `invalidation_conditions`.
- Skip the human-review gate on trade-relevant packets.
- Consume stale convergence artifacts. The M1 freshness check applies.
- Treat private runtime state as public source material.
- Route a question to a packet without resolvable supporting references.
- Convert watchlist rankings into execution instructions.

When freshness, references, or runtime health fail, the correct output is a blocked or demoted packet with an explanation.

## 8. Non-Goals

The metalayer is not a chatbot.

It is not a live trader.

It is not an oracle.

It is not a sentiment engine.

It does not implement brokerage integrations, live order routing, or private credential handling. Those remain private and gated.
