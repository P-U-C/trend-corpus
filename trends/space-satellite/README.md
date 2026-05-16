# Space / Satellite

This theme tracks public-market exposure to commercial space infrastructure.
Mirrors the pattern of `trends/defense-ai/`: sources -> claims -> entities ->
theses -> decision packets, with sector-tuned half-lives and a human-review
gate before any private execution.

## Sector boundary

In scope:
- Launch services and spacecraft manufacturing (Rocket Lab, SpaceX, Firefly)
- Direct-to-device and satellite broadband (AST SpaceMobile, Iridium,
  Globalstar, Viasat, EchoStar / Hughes)
- Earth-observation imagery and analytics (Planet, Maxar)
- Lunar transport and cislunar infrastructure (Intuitive Machines)
- National-security satellite buses, ground systems, and integration
  (Kratos, L3Harris, Lockheed Martin, Northrop Grumman)

Out of scope:
- Pure defense autonomy and unmanned systems without satellite exposure
  (separate defense-ai theme)
- Pure terrestrial telecom carriers, except where they are spectrum partners
  for D2D satellite services
- Astronomy / science missions with no public-company revenue linkage
- Classified programs not visible from public budget docs or contract awards

## Why now

Four structural shifts are running in parallel: FCC Supplemental Coverage from
Space rules moved direct-to-device from waiver-by-waiver experiments toward a
license framework; AST SpaceMobile, SpaceX / Starlink, Iridium, and Globalstar
are turning handset and IoT connectivity into a satellite revenue category;
Rocket Lab, SpaceX, and Firefly are proving launch cadence is a capacity market;
and NRO, SDA, DOD, and NASA are using commercial contract vehicles for imagery,
transport-layer satellites, and lunar deliveries. The checklist catalyst is
"broadband / launch contract" -- read that broadly: any visible inflection in
D2D spectrum access, constellation launch cadence, government imagery awards,
or CLPS / national-security satellite contract flow can reprice the sector.

## What's in this directory

- `trend.yaml` -- theme manifest
- `sources/` -- FCC / NASA / NRO / DOD / company IR / official company feeds
  the runtime ingests
- `claims/` -- 3 example claims demonstrating the category taxonomy
  (regulatory, supply, market). Illustrative, not pulled from a live db.
- `entities/` -- the scanner seeds (RKLB, ASTS, PL, LUNR) plus public adjacents
  and 3 private keystones (entity_type private_company; no ticker_exposures)
- `events/` -- one example regulatory / commercialization event
- `theses/` -- the synthesizing argument
- `decision-packets/` -- one watchlist-candidate packet with substantive
  `invalidation_conditions` and `execution_state: human_review_required`
- `watchlists/` -- the operational signals worth monitoring on cadence
- `docs/prompts.md` -- adapted extract / packet / validate prompts with
  space-satellite vocabulary

## Sector-tuned half-lives

Space moves on regulatory approvals, launch campaigns, and contract vehicles.
The defaults differ from peptides:

| category | half_life_days | why |
|---|---|---|
| regulatory | 90 | FCC spectrum, FAA launch licensing, and ITU coordination can change market access quickly |
| corporate | 60 | contract awards, financings, partnerships, and IPO signals are the main fast clock |
| manufacturing | 365 | satellite bus production, launch cadence, and ground-network deployment are multi-quarter programs |
| market | 365 | broadband ARPU, government imagery contracts, and defense launch demand reset annually or multi-year |
| supply | 180 | phased arrays, Ka / Ku / V-band payloads, solar arrays, RF ASICs, and launch slots bottleneck cadence |
| research | 365 | constellation milestones, optical inter-sat links, and lunar mission learnings are multi-year |

Drop `clinical` and `pricing` -- space pricing is contract-specific and not a
useful aggregate signal at this layer.

## Reusing this for adjacent themes

This theme is similar in shape to `defense-ai` and `nuclear-smr`: a regulated
sector with a government-contract backbone, supply-side bottlenecks, and
milestone-driven market access. Future themes around edge connectivity,
geospatial analytics, or cislunar infrastructure should copy this layout.
