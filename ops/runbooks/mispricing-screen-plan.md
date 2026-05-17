# Mispricing-Screen + Two-Bucket Options Portfolio: Plan

**Status:** plan only -- not yet executed. 30-minute draft.

**Mandate (operator):** make money short-term; pile into long-term thesis
lottery tickets.

## Two-bucket frame

| bucket | horizon | conviction posture | instrument shape | sizing | exit |
|---|---|---|---|---|---|
| **Income** | 0-90 days to catalyst | mispricing-driven; only when thesis-implied move > market-implied move | ATM/near-ATM directional (calls, puts, spreads, straddles around dated events) | 1-2% of options book per trade; max 15 concurrent | pre-set at +50% gain or 1 day pre-catalyst (theta) |
| **Lottery** | 12-24 months out | structural thesis; doesn't need market mispricing today | OTM long calls or LEAPS on theme keystone tickers | $500-$2000 per ticket; 10-20 tickets across themes | hold to expiry unless thesis breaks |

The bucket split is the design center. Income trades pay for the lottery
book; lottery book provides the asymmetric upside that compounding
income can't on its own. Default capital allocation: **60% income / 40%
lottery** (tunable in config).

## What we already have

- `convergence-latest.json` -- 108 scored tickers across 14 themes, with
  conviction tier (HIGH/MEDIUM/LOW), exposure_strength per ticker,
  status per theme, source_claim_ids backing each row.
- Per-theme curated claims (3-4 each, hand-authored + Codex-reviewed)
  with category, half_life_days, evidence_at, confidence.
- Live aggregates flowing daily from 13 sector runtimes.
- IB Gateway live on this box (port 4002, paper mode for now).
- `puc-trading/` repo with `paper-journal/`, `scripts/`, `trades/`.

## What we DON'T have yet

1. **Per-claim event_horizon** -- claims have `date_of_evidence`
   (when we believed it) but not `event_horizon` (when it resolves).
2. **Catalyst calendar** -- consolidated dated-event list per theme
   (earnings, FDA decisions, FOMC, conference launches, M&A close
   targets, regulatory docket deadlines).
3. **Options-chain pull from IB Gateway** -- IBKR is live but no Python
   script today pulls chains for the convergence universe.
4. **Mispricing detector** -- the actual thesis-vs-market gap math.
5. **Two-bucket portfolio shaper** -- sizing logic + concurrency caps
   + bucket rebalancing.
6. **Trade-ticket generator + morning Telegram brief**.

## Plan (6 phases, ~12-15 hours total)

### Phase 0 -- Catalyst calendar + event_horizon enrichment (2-3h)

**Add `event_horizon` as a first-class field on claims.**
- Schema: optional date or date-range field on `claim.schema.json`.
- Backfill 14 themes × 3-4 claims each = ~50 claims with horizon dates.
  Most are inferable from claim text already (Codex review pass already
  surfaced precise dates: Lilly-Verve 2025-07-25, Lattice-AMI close
  2026-Q3, QS Eagle Line 2026-02-04, FOMC dates, etc.).
- For ambiguous claims ("structural multi-year"), use a horizon-bucket
  enum: `near_term_0_90d | mid_term_90d_1y | long_term_1y_3y |
  structural_3y_plus`.

**Build catalyst-calendar.yaml under `~/puc-trading/calendar/`.**
- One entry per dated event:
  ```yaml
  - id: cat_crsp_q3_2026
    theme_id: synthetic-biology
    ticker: CRSP
    event_date: 2026-10-29
    event_type: earnings
    thesis_link: clm_synbio_casgevy_commercial_compounding
    horizon_days_from_today: 165
  ```
- Categories: `earnings | fda_decision | fomc | regulatory_docket |
  ma_close | conference_launch | trial_readout | ipo_rumor |
  budget_appropriation`.
- Initial population: ~80-120 events across 14 themes (manual pass +
  earnings dates from yfinance for the 50 HIGH-tier tickers).

### Phase 1 -- IB Gateway options-chain pull (2h)

`~/puc-trading/options/ib_chain.py`:
- Connects to IB Gateway on port 4002 via `ib_insync`.
- For a ticker, pulls full option chain (all expirations, all strikes).
- Caches to `~/puc-trading/options-cache/<ticker>-<YYYY-MM-DD>.json`.
- Includes: bid, ask, mid, IV, delta, gamma, theta, vega, OI, volume.
- Daily snapshot cron at 16:30 ET (post-market close).
- Smoke test: pull chains for all 108 convergence tickers + handle
  ones IBKR doesn't have (HK / KRX listings — fall back to "no chain").

### Phase 2 -- Mispricing detector (3h)

`~/puc-trading/mispricing/detector.py`:
- For each (ticker, catalyst) pair from the calendar:
  - Find nearest options expiry past `event_date` (within 30 days for
    income, 12-24 months for lottery).
  - Compute **market-implied move** = ATM straddle price / spot at that
    expiry.
  - Compute **thesis-implied move** as a function of:
    - convergence score
    - exposure_strength (per ticker_exposures basis)
    - catalyst_weight from score_components
    - event_type-specific multiplier (earnings: 1.0x, FDA decision: 2.0x,
      M&A close: 1.5x, regulatory ruling: 0.8x)
  - Compute **mispricing ratio** = thesis_move / market_move.
  - Tag as `mispriced_up` (ratio > 1.5), `fair` (0.7-1.5),
    `mispriced_down` (ratio < 0.7), or `no_chain` (IB returned nothing).
- Also computes:
  - Skew (25-delta puts vs calls) -- flag wrong-way pricing
  - Term structure inversion across catalyst date
  - Open-interest density at the thesis strike

Output: `~/puc-trading/mispricing/screen-YYYY-MM-DD.json` with one row
per (ticker, catalyst) pair sorted by mispricing ratio descending.

### Phase 3 -- Portfolio shaper -- two-bucket sizing (2-3h)

`~/puc-trading/portfolio/shaper.py`:

**Income bucket (60% of options budget):**
- Filter screen to `mispriced_up` rows where `horizon_days_from_today
  <= 90`.
- Pick top N (default 10-15) by mispricing ratio × conviction score.
- For each, recommend instrument:
  - Bullish thesis + mispriced_up + skew OK → ATM/slightly-OTM call
    spread dated 1 week post-catalyst
  - Bullish thesis + mispriced_up + skew wrong-way (puts bid) → risk
    reversal (long call, short put, collared by spreads)
  - Mispriced but direction-agnostic → straddle through catalyst
  - Bearish thesis (we add this later when corpus carries bearish
    claims; today most signals are bullish)
- Sizing: 1-2% of options book per trade. Max 15 concurrent.
- Exit rules pre-encoded: +50% gain triggers close; 1 day pre-catalyst
  close if no thesis-relevant news.

**Lottery bucket (40% of options budget):**
- Filter screen to `horizon_days_from_today > 365` AND status in
  {`emerging`, `growing`} AND HIGH tier.
- Pick top N (default 10-20) ranked by `convergence_score × (1 + days_to_horizon/730)`.
- For each, recommend OTM long calls or LEAPS dated 12-24 months out
  at delta 0.20-0.30.
- Sizing: $500-$2000 per ticket, max 20 tickets.
- Exit: hold to expiry unless `clm_*` claims relevant to the ticker
  flip from `active` to `superseded_by` (thesis-break signal).

### Phase 4 -- Daily trade-ticket generator (2h)

`~/puc-trading/portfolio/tickets.py`:
- Reads: convergence-latest, catalyst-calendar, mispricing-screen,
  current paper-journal positions.
- Emits: `~/puc-trading/trades/tickets-YYYY-MM-DD.md` with sections:
  - NEW INCOME (this morning's recommended new positions)
  - NEW LOTTERY (this morning's recommended long-dated adds)
  - CLOSE (positions hitting exit rules)
  - SCALE (existing winners to add to)
  - HOLD (no-action positions, with current P&L)
  - RISK (gross delta / theta / vega; total capital deployed; max loss)
- All recommendations default to `paper-journal` execution. Live
  execution is gated at `human_review_required` (matches B2 packet
  pattern).

### Phase 5 -- Morning Telegram brief (1h)

`~/puc-trading/notify/morning_brief.py`:
- 06:00 ET (10:00 UTC) Telegram.
- Reads tickets-YYYY-MM-DD.md.
- Sends a compressed version of the day's NEW INCOME + NEW LOTTERY
  recommendations + any CLOSE actions.
- Format:
  ```
  [puc-trading] 2026-05-18 morning brief
  INCOME (3 new):
    QS Oct17 $5 calls @ $0.40 (size 1.5%) — thesis 2.1x implied
    LITE Oct24 $90/$100 cs @ $4.10 (size 1.0%) — Q3 catalyst
    IONQ Sep19 $45 straddle @ $7.20 (size 1.0%) — qubit milestone vol play
  LOTTERY (1 new):
    BIOA Jan28 $12 calls @ $0.85 (size $1500) — BGE-102 ramp
  CLOSE: NVDA Aug $135c +52% — hit target
  HOLD: MARA Sep $25c | GEV Dec $200c | ASTS Mar $35c
  RISK: $42k deployed | max-loss $42k | gross-gamma $1.2k/$
  ```

### Phase 6 -- IBKR paper-execution loop (gated, optional, 2h)

Existing IB Gateway can place paper orders. Add:
- Approve-via-Telegram flow: each new ticket has a button-equivalent
  (reply "yes <ticket-id>") that triggers paper-order placement.
- Daily mark-to-market + journal entries in `~/puc-trading/paper-journal/`.
- After 30 days of paper validation, optionally enable a `LIVE_PUSH=1`
  flag that switches paper → real orders.

## Decision points

1. **Capital split**: 60/40 income/lottery, or different?
2. **Total options budget**: how many $ deployed at peak? affects sizing.
3. **Universe**: only convergence HIGH (today 60 tickers), or expand to
   MEDIUM (108 total)?
4. **Live execution gate**: paper-only for 30 days, then enable live?
   Or live from day 1?
5. **Repo placement**: extend `puc-trading` (where convergence-latest
   already lives) or new `puc-mispricing` repo?
   - Default: extend puc-trading.
6. **Bearish exposure**: today the corpus is bullish-only (all
   ticker_exposures are `direction: beneficiary`). Add bearish exposure
   tagging now or defer?

## Risks

| risk | mitigation |
|---|---|
| Thesis-implied move math is hand-wavy | Backtest against last 90 days of post-earnings moves to calibrate the conviction-to-move function before going live |
| Options chains for HKEX / KRX / TSE tickers (Insilico, Idemitsu, Mitsui, Samsung SDI, SK, Toyota TM) unavailable on IB | Skip; or use ADR equivalents (TM, SSNLF); document gaps in trade tickets |
| Catalyst calendar staleness (an earnings date moves) | Calendar refresher cron pulls earnings dates from yfinance daily; FDA/FOMC dates rare to move; Codex review pass already validated big M&A dates |
| Two-bucket sizing collides on a single ticker (income trade + lottery ticket on QS) | Allowed but capped: total ticker exposure across both buckets ≤ 5% of options book |
| Mispricing detected but options too illiquid to trade | Filter: minimum daily volume > 100 contracts, bid-ask < 10% of mid; fall back to next-best strike |
| Paper-trade tracking diverges from live (fills not perfect mid) | Track slippage column in paper-journal; calibrate sizing for assumed 1-3% slippage on entry/exit |

## Estimate

- Phase 0: 2-3h (catalyst calendar + event_horizon backfill)
- Phase 1: 2h (IB Gateway chain pull)
- Phase 2: 3h (mispricing detector)
- Phase 3: 2-3h (portfolio shaper)
- Phase 4: 2h (ticket generator)
- Phase 5: 1h (morning brief)
- Phase 6: 2h (optional paper-execution loop)
- **Total: ~12-15 hours of focused work.**

Phases 0-5 give the daily "what to trade" output without any auto-execution.
Phase 6 closes the loop to actual paper-trade tracking and (eventually,
gated) live execution.

## What I'd do first if green-lit

1. Phase 0 first (2-3h) -- catalyst calendar + event_horizon. This is
   pure data work; gives us the input every other phase needs.
2. In parallel, smoke-test IB Gateway chain pull on 5 tickers (1h) --
   validates the data pipe and surfaces "no chain for HKEX listings"
   early.
3. Then Phase 2+3+4 in sequence (7-8h) to get the daily ticket
   generator running end-to-end on paper.
4. Phase 5 + Phase 6 once the tickets look sane on paper for a week.

Send back: capital split, total budget, universe scope, repo placement.
I start Phase 0 on the next message.
