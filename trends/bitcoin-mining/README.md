# Bitcoin Mining

This theme tracks public-market exposure to industrial Bitcoin mining.
Mirrors the pattern of `trends/space-satellite/`: sources -> claims ->
entities -> theses -> decision packets, with sector-tuned half-lives and a
human-review gate before any private execution.

## Sector boundary

In scope:
- Pure-play public Bitcoin miners (MARA, Riot, CleanSpark, Bitfarms, Cipher)
- Power-first miners with AI / HPC conversion optionality (Hut 8, TeraWulf,
  IREN, Core Scientific, Bit Digital, HIVE)
- Lower-scale or distressed listed miners where the ticker still screens
  (Argo Blockchain)
- ASIC manufacturers and supply-chain bottlenecks (Bitmain, MicroBT, Canaan)
- Power-market and state-level regulation that changes effective realized
  hashrate, especially ERCOT and New York

Out of scope:
- Non-Bitcoin proof-of-stake networks and staking services
- Exchanges, wallets, custodians, and brokerages without mining exposure
- Consumer GPU mining and retail hobbyist equipment
- Private pool routing, firmware exploitation, facility security, or
  non-public power-contract details

## Why now

Three structural shifts are running in parallel: the 2024 halving reduced block
subsidy to 3.125 BTC, pushing hashprice and fleet efficiency into the center of
miner economics; U.S. state and grid rules are turning power access, large-load
registration, and curtailment economics into gating variables; and public miners
are splitting between pure-play BTC production and AI / HPC data-center
conversion. The checklist catalyst is "next BTC cycle" -- read that broadly:
hashprice recovery, BTC spot-price durability, tariff / ASIC supply shocks, or
hyperscaler lease flow can move the group faster than quarterly mining output.

## What's in this directory

- `trend.yaml` -- theme manifest
- `sources/` -- miner IR / ASIC vendor / hashprice / state-regulatory feeds
  the runtime ingests
- `claims/` -- 3 example claims demonstrating the category taxonomy
  (regulatory, supply, market). Illustrative, not pulled from a live db.
- `entities/` -- the scanner seeds (MARA, RIOT, CLSK) plus public adjacents
  and 2 private ASIC keystones (entity_type private_company; no
  ticker_exposures)
- `events/` -- one example regulatory / operating-capacity event
- `theses/` -- the synthesizing argument
- `decision-packets/` -- one watchlist-candidate packet with substantive
  `invalidation_conditions` and `execution_state: human_review_required`
- `watchlists/` -- the operational signals worth monitoring on cadence
- `docs/prompts.md` -- adapted extract / packet / validate prompts with
  bitcoin-mining vocabulary

## Sector-tuned half-lives

Bitcoin mining moves on hashprice, power pricing, ASIC cycles, and regulatory
access. The defaults differ from space-satellite:

| category | half_life_days | why |
|---|---|---|
| regulatory | 60 | SEC / CFTC / IRS guidance, state moratoria, ERCOT rules, and EPA scrutiny can change site economics quickly |
| corporate | 60 | M&A, hosting agreements, capacity expansions, AI / HPC pivots, and financing marks move on quarterly cadence |
| manufacturing | 180 | ASIC release cycles and fleet upgrades reset efficiency over half-year windows |
| market | 90 | hashrate, network difficulty, miner economics, BTC price, and treasury value rotate quickly |
| supply | 180 | ASIC concentration, chip fabrication, tariffs, and delivery schedules bottleneck fleet upgrades |
| pricing | 30 | hashprice and electricity spreads are fast-moving operating inputs |

Drop `clinical` and `research` entirely -- Bitcoin mining is cyclical,
infrastructure-driven, and pricing-sensitive.

## Reusing this for adjacent themes

This theme is similar in shape to `ai-infrastructure` and `space-satellite`:
regulated capacity, scarce hardware, power-market exposure, and contract-flow
signals. Future data-center power themes should copy this layout but separate
Bitcoin hashprice beta from AI / HPC lease-duration economics.
