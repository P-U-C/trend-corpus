# Scanner Feed: Runtime → Aggregates → Convergence → Scanner

End-to-end overview of how runtime data lands on the public scanner
dashboard at `pft.permanentupperclass.com/scanner/`.

## Pipeline

```
city-worker-301 (13 sector runtime users)
   ↓ (extract claims via Claude every 6h)
   db.sqlite (per-user)
   ↓ (export-aggregates at 13:30-13:42 UTC daily, staggered +1min per user)
   theme-runtime aggregates.py (schema-validated, secret-scanned)
   ↓ (commit + push)
   trend-corpus:trends/<theme>/aggregates/<theme>-aggregates.json
                                ↑
                                also: peptide runtime publishes via separate
                                sync-peptides-aggregates.sh (legacy pull pattern)
                                ↓
clawd (orchestration, 13:55 UTC daily)
   git pull trend-corpus
   ↓
   for each of 14 themes:
     generate_opportunities.py --theme <slug> --themes-dir ~/trend-corpus/trends
     → ~/trend-intel-private/themes/<slug>/artifacts/opportunity-rows.json
   ↓
   for each of 14 themes:
     merge_convergence.py --opportunity-source <opportunity-rows.json>
   → ~/puc-trading/corpus/convergence-latest.json (merged baseline)
   ↓ (commit + push if DEPLOY_PUSH=1)
   puc-trading:corpus/convergence-latest.json
   ↓
scanner / dashboard refresh
```

## Cron timings (UTC)

| time | host | what |
|---|---|---|
| 00:00 / 06:00 / 12:00 / 18:00 | city-worker-301 (all sector users) | ingest sources |
| 00:15 / 06:15 / 12:15 / 18:15 | city-worker-301 | extract with Claude (limit 50/run) |
| 05:00 | city-worker-301 | sync (`git pull` trend-corpus, rebuild sources.txt + prompts/) |
| 13:30 | city-worker-301 ai-infra | export-aggregates + commit + push trend-corpus |
| 13:31 | city-worker-301 quantum | "" |
| 13:32 | city-worker-301 nuclear | "" |
| 13:33 | city-worker-301 robotics | "" |
| 13:34 | city-worker-301 defense | "" |
| 13:35 | city-worker-301 space | "" |
| 13:36 | city-worker-301 bitcoin | "" |
| 13:37 | city-worker-301 bci | "" |
| 13:38 | city-worker-301 solidstate | "" |
| 13:39 | city-worker-301 synbio | "" |
| 13:40 | city-worker-301 edgeai | "" |
| 13:41 | city-worker-301 photonic | "" |
| 13:42 | city-worker-301 longevity | "" |
| 13:55 | clawd | refresh-convergence.sh → merge + push puc-trading |
| 14:00 | city-worker-301 (all) | notify digest (Telegram) |

Stagger is +1 min per user so concurrent push race never has 13
clients pushing at the same instant. The `publish_aggregates()` helper
does one push-retry on `non-fast-forward` rejection.

## Outputs at each stage

| location | shape | producer |
|---|---|---|
| `~/<theme>-corpus/db.sqlite` (city-worker) | private claims table | extract.py |
| `~/<theme>-corpus/out/<theme>-aggregates.json` (city-worker) | aggregate-only public view | theme_runtime aggregates.py |
| `~/trend-corpus/trends/<theme>/aggregates/<theme>-aggregates.json` (everywhere) | published aggregates, schema-validated | publish_aggregates() in sync.py |
| `~/trend-intel-private/themes/<theme>/artifacts/opportunity-rows.json` (clawd) | per-theme weighted ticker rows | generate_opportunities.py |
| `~/puc-trading/corpus/convergence-latest.json` (clawd, public via push) | merged convergence baseline | merge_convergence.py |
| `pft.permanentupperclass.com/scanner/scan-results.json` | rendered scanner state | scanner consumer |

## Manual operator commands

### Trigger one runtime to publish now
```bash
ssh city-worker-peptides "sudo -iu ai-infra bash /home/ai-infra/aifra-export.sh"
```
Replace `ai-infra` with the user slug.

### Refresh convergence + push locally
```bash
DEPLOY_PUSH=1 bash ~/trend-corpus/scripts/refresh-convergence.sh
```

### Inspect what's flowing
```bash
# All recent aggregates commits on trend-corpus origin
git -C ~/trend-corpus log --oneline -20 -- 'trends/*/aggregates/'

# Latest convergence on puc-trading
python3 -c "
import json
d = json.load(open('$HOME/puc-trading/corpus/convergence-latest.json'))
print(f'generated_at: {d[\"generated_at\"]}')
print(f'themes: {len(d[\"themes\"])}')
print(f'scores: {len(d[\"scores\"])}')
for s in sorted(d['scores'], key=lambda r: -r.get('score', 0))[:15]:
    print(f'  {s[\"theme_id\"]:>22} {s[\"ticker\"]:>6} {s[\"score\"]:.4f} {s[\"tier\"]}')
"
```

### Tail aggregates logs on city-worker
```bash
ssh city-worker-peptides "sudo tail -50 /home/ai-infra/logs/ai-infra-aggregates.log"
```

## Failure modes + recovery

| failure | symptom | recovery |
|---|---|---|
| Push token rotated | All 13 sector runtimes fail to push; aggregates files stale on trend-corpus | Re-run `/tmp/deploy-aggregates-all.sh` on city-worker with the new token; pulls latest + re-embeds remote URL |
| One runtime's db.sqlite missing | One theme's aggregates JSON contains 0 claims | Check user's ingest+extract cron, re-init db if needed (`python3 -m theme_runtime init`) |
| trend-corpus CI rejects an aggregates push | Runtime's `aggregates` step errors `schema validation failed` | Inspect the offending JSON; usually a fix at `runtime/theme_runtime/aggregates.py` |
| 13 concurrent pushes race past the stagger | One runtime's push fails after retry | `aggregates` log on the affected user; next cron firing will retry idempotently |
| Convergence merge produces dupes | scanner shows `theme_x` and `theme-x` as separate themes | The orchestrator already has a snake → kebab normalizer; bug is in `populate_convergence.py` reseeding fixtures |
| Stale convergence-latest on dashboard | scanner page header timestamp >24h old | Check clawd cron `55 13 * * *`; manually run `DEPLOY_PUSH=1 bash refresh-convergence.sh` |

## Security envelope

- Aggregates JSON contains counts + lowercased slugs only -- never raw
  claim text, never per-claim confidence, never date_of_evidence per
  claim, never supersedence relationships.
- Secret-pattern scan applied at every publish boundary.
- Schema validation enforced at three places: exporter write,
  publish-time, CI validate.
- Push token is fine-grained, scoped only to P-U-C/trend-corpus
  contents:write. Compromise on one runtime user = compromise of
  trend-corpus content writes, but not of any other resource.
- Trade-action denylist (place_order, order_type, etc.) prevents any
  YAML escaping into the public corpus via the validator.

## Related runbooks

- `peptides-aggregates-bridge.md` -- legacy peptide-only pull pattern
  (still active on city-worker-301; will eventually be cut over to the
  generic path)
- `sector-aggregates-bridge-plan.md` -- the implementation plan for
  this bridge
- `add-new-theme.md` -- when adding a 15th sector, mirror the deploy
  flow described here
