# Robotics / Humanoid

Robotics / Humanoid covers public-market exposure to embodied automation and
the industrial stack needed to scale it. In scope: humanoid platforms such as
Optimus, Figure, Apollo, Digit, Phoenix, and Atlas; surgical, industrial,
warehouse, and delivery robots; collaborative robots; robotic vision and
perception; actuators, harmonic drives, motors, rare-earth magnets, end
effectors, tactile sensors, and AI software stacks for embodied agents.

Out of scope: autonomous vehicles as a separate transport theme, drones where
the thesis is primarily defense autonomy, pure software AI without embodiment,
general industrial software, and consumer electronics with no material robotics
exposure. Medical robotics is included through robotic procedure volume and
installed base, but clinical-efficacy claims are not the main taxonomy here.

## Architecture Decisions

This directory mirrors the nuclear-SMR, quantum-computing, and
AI-infrastructure shapes so non-peptide sectors remain uniform. Public objects
are source inventories and example claims, not a live private research
database. Claims are synthetic but specific illustrations of how a runtime
would extract and refresh evidence from public sources.

The theme is set to `growing` because the public signal is no longer only lab
demos: Figure, Tesla, Apptronik, Symbotic, Serve, and surgical robotics
incumbents are now putting robots into production, pilot, or commercial service
contexts. The highest-value evidence is therefore operational: pilot counts,
unit economics, actuator supply, safety standards, factory adoption, fleet
growth, procedure volume, and private humanoid financing or IPO timing.

Trade-relevant outputs remain gated at `human_review_required`. Watchlists
describe what to monitor; decision packets describe why a watchlist may be
useful; neither is an instruction to transact.

## Folder Responsibilities

- `sources/` inventories public URLs suitable for ingestion: safety standards,
  company IR surfaces, private developer announcements, supplier pages, and
  robotics trade sources.
- `claims/` provides example atomic claims across corporate, manufacturing,
  and market categories.
- `entities/` maps public companies to ticker exposure, exchange, role, and
  exposure basis; private humanoid developers are represented without ticker
  exposure.
- `events/` records a concrete robotics milestone that can anchor
  time-sensitive claims.
- `theses/` combines claims into a sector-level argument.
- `decision-packets/` contains a human-review watchlist verdict with
  observable invalidation conditions.
- `watchlists/` defines the public monitoring checklist for the sector.
- `docs/prompts.md` adapts the peptides extraction, packet, and validation
  prompts to robotics and humanoid vocabulary.

## Privacy And Reuse

This public corpus may name public companies, public URLs, public standards,
and public sector claims. It must not include robot-control implementation
details, safety bypasses, fleet-routing instructions, private customer
deployment data, paid-source leaks, private packet questions, non-public model
transcripts, positions, account identifiers, or execution details. Private
scanners can consume these objects through documented file boundaries, but
working intelligence and operator-specific state belong outside this repo.

The directory follows the established non-peptide template: 10-15 sources,
8-15 entities when the scanner has ticker join keys, 3 example claims, one
thesis, one gated decision packet, one watchlist, and adapted prompts.
