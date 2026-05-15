# Quantum Computing

Quantum Computing covers public-market exposure to quantum hardware and the
industrial stack needed to scale it. In scope: trapped-ion systems,
superconducting qubits, quantum annealing, photonic quantum processors,
neutral-atom approaches, cryogenic systems, control electronics, quantum cloud
access, benchmark publications, quantum networking, and listed companies whose
equity narrative is materially tied to quantum milestones.

Out of scope: classical "quantum-inspired" optimization software with no
hardware dependency, post-quantum cryptography vendors as a standalone trade,
academic or government labs without listed exposure, generic cybersecurity
names, and large technology companies where quantum work is too small to move
the ticker unless it changes the broader platform narrative. NIST
post-quantum standards still matter as a policy and urgency signal, but they
are not treated as a separate cryptography-vendor theme here.

## Architecture Decisions

This directory mirrors the AI infrastructure shape so future non-peptide
sectors can stay uniform. Public objects are source inventories and example
claims, not a live private research database. Claims are synthetic but
specific illustrations of how a runtime would extract and refresh evidence
from public sources.

The theme is set to `peak_hype` because the seed public quantum tickers can
move on milestones before there is durable commercial revenue. That makes the
most useful evidence different from a mature infrastructure cycle: the corpus
focuses on benchmark quality, supply-chain constraints, export controls, cash
runway, and whether large platform companies convert research milestones into
cloud-access or vendor demand.

Trade-relevant outputs remain gated at `human_review_required`. Watchlists
describe what to monitor; decision packets describe why a watchlist may be
useful; neither is an instruction to transact.

## Folder Responsibilities

- `sources/` inventories public URLs suitable for ingestion: policy pages,
  company IR surfaces, official milestone posts, suppliers, and research
  trackers.
- `claims/` provides example atomic claims across regulatory, manufacturing,
  and market categories.
- `entities/` maps public companies to ticker exposure, exchange, role, and
  exposure basis; private companies are represented without ticker exposure.
- `events/` records a concrete quantum milestone that can anchor time-sensitive
  claims.
- `theses/` combines claims into a sector-level argument.
- `decision-packets/` contains a human-review watchlist verdict with
  observable invalidation conditions.
- `watchlists/` defines the public monitoring checklist for the sector.
- `docs/prompts.md` adapts the peptides extraction, packet, and validation
  prompts to quantum-computing vocabulary.

## Privacy And Reuse

This public corpus may name public companies, public URLs, and public sector
claims. It must not include customer-specific procurement data, controlled
technical implementation details, paid-source leaks, private packet questions,
non-public model transcripts, positions, account identifiers, or execution
details. Private scanners can consume these objects through documented file
boundaries, but working intelligence and operator-specific state belong
outside this repo.

The directory is intended to match the AI infrastructure template closely:
10-15 sources, 6-12 entities when the scanner has ticker join keys, 3 example
claims, one thesis, one gated decision packet, one watchlist, and adapted
prompts.
