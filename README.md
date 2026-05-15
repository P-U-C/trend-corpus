# trend-corpus

Public template for building sector decision corpora that agents can
maintain, validate, and hand off to private runtimes through file
boundaries.

The shape is: **sources -> claims -> theses -> decision packets**, with
append-only supersedence, category-driven half-lives, and a human-review
gate before any private execution. The pattern is proven on a live
peptide-industry runtime; this repo publishes the methodology so other
sectors can spin up the same shape.

See [`docs/architecture.md`](docs/architecture.md) for the design and
[`docs/new-sector-research-workflow.md`](docs/new-sector-research-workflow.md)
for the agent-driven theme-spinup pattern.

## Repo map

```
trend-corpus/
|-- README.md                       <-- you are here
|-- AGENTS.md                       <-- Claude orchestrator + Codex implementer split
|-- CONTRIBUTING.md
|-- SECURITY.md                     <-- what NEVER goes in + secret-pattern set
|-- LICENSE                         <-- MIT
|-- CHANGELOG.md
|-- Makefile                        <-- validate / test / populate-convergence / scan / up / down
|-- .env.example
|-- .github/workflows/validate.yml  <-- CI: make validate + make test on push/PR
|
|-- docs/
|   |-- architecture.md             # how the pieces fit (the design doc)
|   |-- theme-authoring.md          # how to add a new theme by hand
|   |-- new-sector-research-workflow.md  # how Claude + Codex spin up a new theme
|   |-- metalayer.md                # cross-theme decision service spec
|   |-- llm-convergence.md          # walkthrough of the convergence method theme
|   |-- peptide-example.md          # walkthrough of the canonical peptides theme
|   `-- operations.md
|
|-- schemas/
|   |-- trend.schema.json
|   |-- source.schema.json
|   |-- claim.schema.json
|   |-- entity.schema.json
|   |-- event.schema.json
|   |-- thesis.schema.json
|   |-- decision-packet.schema.json
|   |-- watchlist.schema.json
|   |-- convergence.schema.json     # for the M1 scanner seam artifact
|   `-- aggregates.schema.json      # for live-runtime aggregate exports (Decision 2)
|
|-- taxonomy/
|   |-- claim-categories.yaml       # regulatory / pricing / corporate / manufacturing / market / clinical / methodology
|   |-- execution-states.yaml       # research_only / watchlist_candidate / human_review_required / approved_for_private_execution
|   |-- theme-status.yaml           # emerging / growing / peak_hype / post_peak
|   `-- tiers.yaml                  # HIGH / MEDIUM / LOW
|
|-- trends/                         <-- THIS is where sector themes live
|   |-- _template/                  # copy this when starting a new theme
|   |-- peptides/                   # canonical reference theme (filled)
|   `-- llm-convergence/            # method theme for the cross-model attention signal
|
|-- packages/corpus-validator/      <-- stdlib-only Python validator
|   |-- corpus_validator/
|   `-- tests/
|
|-- apps/                           <-- placeholder service stubs (M4)
|   |-- metalayer-api/              # typed decision service HTTP stub
|   `-- mcp-server/                 # MCP server stub
|
|-- ops/
|   |-- docker-compose.yml
|   `-- runbooks/
|       |-- install.md
|       |-- add-new-theme.md
|       |-- scanner-integration.md
|       |-- deploy-cadence.md
|       `-- peptides-aggregates-bridge.md
|
`-- tests/test_repo_smoke.py        # CI smoke: every trend.yaml validates + no secrets + refs resolve
```

## Quick start

```bash
git clone https://github.com/P-U-C/trend-corpus.git
cd trend-corpus
python3 -m pip install pyyaml pytest
make validate
make test
```

To add a new theme by hand:

```bash
cp -r trends/_template trends/<your-sector>
$EDITOR trends/<your-sector>/trend.yaml
# add source / claim / entity / thesis / decision-packet / watchlist objects
make validate
```

To use the agent-spinup workflow, see
[`docs/new-sector-research-workflow.md`](docs/new-sector-research-workflow.md).

## Theme coverage (LLM Convergence Scanner sectors)

The convergence scanner ranks options across 14 themes. Each one should
get a full peptides-style theme directory here: 8-15 sources, 2-3 example
claims demonstrating the taxonomy, 2-3 entities with tickers, 1 thesis,
1 decision packet with substantive `invalidation_conditions` and
`execution_state: human_review_required`, 1 watchlist.

Run order is **one at a time** with deep research and review per theme,
not batched. Each theme gets its own commit and review pass.

| # | Theme | Status | Notes |
|---|---|---|---|
|  1 | peptides | **[x] Done** (canonical reference) | Mirrors the live peptide-corpus runtime; verbatim extract/packet/validate prompts + aggregate-only bridge contract. |
|  2 | llm-convergence | **[x] Done** (method theme) | Documents the cross-model attention signal as a theme in its own right. |
|  3 | quantum-computing | [ ] Pending | IONQ, QBTS, RGTI; catalyst = next qubit milestone. |
|  4 | ai-infrastructure | [ ] Pending | NVDA, AVGO, VRT, ANET, MU, TSM, DELL; peak_hype. |
|  5 | nuclear-smr | [ ] Pending | BWXT, OKLO, SMR, GEV, CEG, CCJ, LEU; catalyst = policy / data-center PPA. |
|  6 | robotics-humanoid | [ ] Pending | TSLA, ISRG, SYM, SERV; catalyst = Figure AI IPO / Optimus milestone. |
|  7 | defense-ai | [ ] Pending | PLTR, LDOS; catalyst = government autonomy contract. |
|  8 | space-satellite | [ ] Pending | RKLB, ASTS, PL, LUNR; catalyst = broadband / launch contract. |
|  9 | bitcoin-mining | [ ] Pending | MARA, RIOT, CLSK; post_peak. |
| 10 | bci-neurotech | [ ] Pending | BFLY, QSI; emerging; catalyst = Neuralink / Synchron / Merge IPO. |
| 11 | solid-state-battery | [ ] Pending | QS, SLDP; emerging; catalyst = first commercial shipment. |
| 12 | synthetic-biology | [ ] Pending | CRBU, TWST, PACB; emerging; catalyst = next CRISPR approval. |
| 13 | edge-ai | [ ] Pending | AMBA; emerging; catalyst = on-device AI chip partnership. |
| 14 | photonic-computing | [ ] Pending | LITE, COHR; emerging; catalyst = photonic chip commercialization. |
| 15 | longevity | [ ] Pending | ABBV, CELH; emerging; catalyst = longevity drug breakthrough. |

(Total 15 -- peptides + llm-convergence are the two seed themes; the 13
remaining map 1:1 to the convergence scanner's market-tracking themes.)

Updates land as individual commits with messages like
`theme(quantum-computing): initial seed corpus`. After each theme is
merged, the corresponding row is ticked in this table.

## How a new theme gets researched

Each theme goes through this loop **one at a time**:

1. **Sector definition** -- a paragraph on what the theme covers, what is
   in scope vs out.
2. **Source discovery** (Codex in research mode, web access) -- 8-15
   primary URLs with bucket classification (regulatory primary, company
   IR, trade press, government).
3. **Entity inventory** -- the 5-10 public companies most directly
   exposed, with tickers and roles.
4. **Example claim authoring** -- 2-3 claims that demonstrate the
   category taxonomy (regulatory / manufacturing / market / clinical /
   pricing / corporate) without leaking any private state.
5. **Thesis synthesis** -- one paragraph tying the claims together,
   pointing at the structural argument that makes the theme tradeable.
6. **Decision packet** -- one packet with verdict, supporting theses,
   substantive `invalidation_conditions`, and `execution_state:
   human_review_required` (NEVER `approved_for_private_execution` in
   public corpus).
7. **Watchlist** -- the operational signals worth monitoring on cadence.
8. **Prompts** -- adapt `trends/peptides/docs/prompts.md` to the sector's
   vocabulary if the runtime will mirror that pattern.
9. **Validate + commit** -- `make validate && make test`, commit, push,
   tick the table in this README, move to the next.

Where they run: in the supervised Codex screen on the private orchestration
box, using research-mode access to public web sources. Outputs are
reviewed against the schema + secrets policy before commit. See
[`docs/new-sector-research-workflow.md`](docs/new-sector-research-workflow.md)
for the full pattern and [`AGENTS.md`](AGENTS.md) for the orchestrator /
implementer split.

## Companion repos

- [`puc-trading`](https://github.com/P-U-C/puc-trading) -- private. The
  live scanner runtime that consumes a corpus artifact via the file seam.
- [`pft-validator`](https://github.com/P-U-C/pft-validator) -- public.
  Hosts the live dashboard at `pft.permanentupperclass.com/scanner/`.

## Boundaries

- Trade-relevant outputs MUST carry `execution_state: human_review_required`.
- `approved_for_private_execution` MUST NEVER appear in any public corpus
  object. The validator enforces this.
- No raw private claim text, no operator-specific positions, no
  credentials. See [`SECURITY.md`](SECURITY.md).
- The aggregate-only bridge for live runtimes (peptides today, other
  themes later) is documented at
  [`ops/runbooks/peptides-aggregates-bridge.md`](ops/runbooks/peptides-aggregates-bridge.md).
