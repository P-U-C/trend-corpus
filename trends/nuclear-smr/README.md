# Nuclear / SMR

Nuclear / SMR covers public-market exposure to the next buildout of nuclear
power. In scope: small modular reactor developers, advanced reactor platforms,
large nuclear equipment incumbents, uranium miners, conversion and enrichment,
fuel fabrication, HALEU supply, nuclear-exposed utilities, and data-center
power purchase agreements that create contracted demand for firm carbon-free
power.

Out of scope: nuclear weapons and defense deterrence, fusion, nuclear
medicine, general electric-grid equipment without nuclear exposure, and
uranium exploration narratives with no credible route to utility fuel supply.
The theme treats hyperscaler demand as a market catalyst, but the investable
stack is still constrained by licensing, project execution, fuel availability,
and utility balance sheets.

## Architecture Decisions

This directory mirrors the quantum-computing and AI-infrastructure shape so
non-peptide sectors remain uniform. Public objects are source inventories and
example claims, not a live private research database. Claims are synthetic but
specific illustrations of how a runtime would extract and refresh evidence
from public sources.

The theme is set to `growing` because the market signal is no longer only
policy rhetoric: Microsoft, Amazon, Google, and data-center operators are now
signaling demand for nuclear-backed power, while NRC licensing and HALEU
availability determine what can actually be delivered. That makes the key
public evidence more operational than narrative: PPA flow, licensing dockets,
fuel-cycle commitments, uranium and enrichment pricing, and pure-play runway.

Trade-relevant outputs remain gated at `human_review_required`. Watchlists
describe what to monitor; decision packets describe why a watchlist may be
useful; neither is an instruction to transact.

## Folder Responsibilities

- `sources/` inventories public URLs suitable for ingestion: regulatory pages,
  company IR surfaces, official PPA announcements, developer newsrooms, and
  trade-press monitors.
- `claims/` provides example atomic claims across regulatory, supply, and
  market categories.
- `entities/` maps public companies to ticker exposure, exchange, role, and
  exposure basis; private developers are represented without ticker exposure.
- `events/` records a concrete PPA or licensing milestone that can anchor
  time-sensitive claims.
- `theses/` combines claims into a sector-level argument.
- `decision-packets/` contains a human-review watchlist verdict with
  observable invalidation conditions.
- `watchlists/` defines the public monitoring checklist for the sector.
- `docs/prompts.md` adapts the peptides extraction, packet, and validation
  prompts to nuclear and SMR vocabulary.

## Privacy And Reuse

This public corpus may name public companies, public URLs, public dockets, and
public sector claims. It must not include controlled technical implementation
details, nuclear-material handling instructions, licensing drafting, paid-source
leaks, private packet questions, non-public model transcripts, positions,
account identifiers, or execution details. Private scanners can consume these
objects through documented file boundaries, but working intelligence and
operator-specific state belong outside this repo.

The directory follows the established non-peptide template: 10-15 sources,
8-15 entities when the scanner has ticker join keys, 3 example claims, one
thesis, one gated decision packet, one watchlist, and adapted prompts.
