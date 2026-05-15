# AI Infrastructure

AI Infrastructure covers the physical and financial rails behind large-scale
AI compute. In scope: accelerator GPUs and alternatives, custom AI ASICs,
foundry leading-node supply, advanced packaging, HBM and data-center memory,
Ethernet and optical networking, rack-scale connectivity, AI server assembly,
liquid cooling, power conversion, thermal management, and data-center
electrical infrastructure. The theme treats cloud and hyperscaler demand as a
primary demand channel, but the corpus is about the enabling infrastructure,
not software-only AI applications.

Out of scope: consumer devices, general enterprise SaaS, model labs without a
clear infrastructure supply-chain link, crypto mining hardware except where it
reuses the same power/cooling stack, and generic "AI beneficiaries" whose
exposure is mostly sentiment. The goal is to keep the public theme close to
observable bottlenecks: what has to be built, supplied, powered, cooled,
connected, and regulated for AI data centers to expand.

## Architecture Decisions

This directory follows the peptides reference theme shape so future sectors
can repeat it without special cases. Public objects are examples and source
inventories, not a live private research database. Claims are synthetic but
specific illustrations of the taxonomy, sourced to public URLs and designed to
show how the runtime would extract, refresh, and supersede evidence.

The theme is set to `peak_hype` because AI infrastructure is already heavily
covered by markets, media, and public-company guidance. That status changes the
kind of evidence that matters: the most useful signals are not "AI is growing"
but whether constraints are tightening or easing. The initial corpus therefore
weights export controls, HBM and advanced packaging, hyperscaler demand
pull-through, and power/cooling backlog.

Trade-relevant outputs remain gated at `human_review_required`. Watchlists
describe what to monitor; decision packets describe why a watchlist may be
useful; neither is an instruction to transact.

## Folder Responsibilities

- `sources/` inventories public URLs suitable for ingestion: policy pages,
  company IR surfaces, and trade/research sources.
- `claims/` provides example atomic claims across regulatory,
  manufacturing, and market categories.
- `entities/` maps public companies to ticker exposure, exchange, role, and
  exposure basis.
- `events/` records a concrete event that can anchor time-sensitive claims.
- `theses/` combines claims into a sector-level argument.
- `decision-packets/` contains a human-review watchlist verdict with
  observable invalidation conditions.
- `watchlists/` defines the public monitoring checklist for the sector.
- `docs/prompts.md` adapts the peptides extraction, packet, and validation
  prompts to AI infrastructure vocabulary.

## Privacy And Reuse

This public corpus may name public companies, public URLs, and public sector
claims. It must not include customer-specific procurement data, paid-source
leaks, private packet questions, non-public model transcripts, positions,
account identifiers, or execution details. Private scanners can consume these
objects through documented file boundaries, but working intelligence and
operator-specific state belong outside this repo.

The directory is intended as the first non-peptide template. Future sectors
should keep the same object count and reference discipline: 8-15 sources,
5-10 entities when the scanner has ticker join keys, 2-3 example claims, one
thesis, one gated decision packet, one watchlist, and adapted prompts.
