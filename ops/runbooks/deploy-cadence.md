# Deploy Cadence Runbook

This runbook describes how to publish fresh private scanner results to the
public dashboard without exposing private artifacts.

The deploy path is intentionally narrow:

```text
private convergence artifact -> private scanner -> public scan-results.json -> dashboard repo
```

The public repo documents the shape. The private runtime performs the scan.

## 1. Recommended Cadence

Run the full convergence and scanner publish flow daily.

Recommended time:

```text
14:30 UTC
```

Daily is the default because convergence does not move hour to hour. Hourly
publishes create operational noise without adding much signal.

Use a more frequent scanner-only cadence only when the private operator has a
clear market-data reason and the convergence artifact freshness check remains
strict.

## 2. Cron Line

Keep the cron disabled until the operator has validated the private runtime
manually.

Copy-paste candidate:

```cron
# 30 14 * * * cd /home/ubuntu/puc-trading && RUN_FULL_SCAN=1 DEPLOY_PUSH=1 DEPLOY_MAX_SCAN_AGE_HOURS=48 bash scripts/deploy-scanner-results.sh >> /home/ubuntu/puc-trading/logs/deploy-scanner-results.log 2>&1
```

For publish-only mode after a manual scan:

```cron
# 45 14 * * * cd /home/ubuntu/puc-trading && DEPLOY_PUSH=1 DEPLOY_MAX_SCAN_AGE_HOURS=48 bash scripts/deploy-scanner-results.sh >> /home/ubuntu/puc-trading/logs/deploy-scanner-results.log 2>&1
```

Create the log directory before enabling cron:

```sh
mkdir -p /home/ubuntu/puc-trading/logs
```

## 3. Environment Variables

`RUN_FULL_SCAN`

Set to `1` to run the private scanner before publishing. If unset, the deploy
script assumes `~/pft-validator/scanner/scan-results.json` was refreshed by an
earlier scanner run.

`DEPLOY_PUSH`

Set to `1` to push the dashboard repo after commit. If unset, the script stages
and commits locally, then prints that it would push.

This default is deliberate. No push happens unless the operator opts in.

`DEPLOY_MAX_SCAN_AGE_HOURS`

Maximum accepted age for `scan_meta.scanned_at`. Default is `48`.

Use a lower value for a more aggressive freshness policy. Use a higher value
only for planned downtime or manual recovery.

## 4. Pre-Deploy Preflight

Before enabling a scheduled deploy, check:

- IB Gateway is running and reachable by the private scanner.
- The private convergence artifact exists.
- The convergence artifact passes private validation.
- `~/pft-validator/scanner/scan-results.json` parses as JSON.
- Dashboard shape check passes.
- Secret scan is clean.
- Git status in `~/pft-validator` contains only intended dashboard changes.
- `~/pft-validator/.gitignore` ignores local IB Gateway files.
- No private runtime artifact is staged.
- `DEPLOY_PUSH=1` is set only when a real publish is intended.

Commands:

```sh
cd /home/ubuntu/puc-trading
make validate
python3 scripts/check-dashboard-shape.py
bash scripts/deploy-scanner-results.sh
```

## 5. Freshness Rules

The deploy script reads:

```text
scan_meta.scanned_at
```

The timestamp must parse as an ISO 8601 value or an accepted UTC timestamp
format. It must be newer than `DEPLOY_MAX_SCAN_AGE_HOURS`.

If the scan is stale, the script refuses to commit.

Do not bypass this check. A stale dashboard is worse than a failed deploy
because it looks current to readers.

## 6. Detecting A Stale Dashboard

The dashboard page should expose the last scan time in the page footer.

To inspect the public JSON directly:

```sh
curl -s https://pft.permanentupperclass.com/scanner/scan-results.json | python3 -m json.tool | head -40
```

Look for:

```text
scan_meta.scanned_at
```

If the footer or JSON timestamp is older than the expected cadence, treat the
dashboard as stale.

## 7. Manual Publish Flow

Use this flow when running without cron:

```sh
cd /home/ubuntu/puc-trading
make validate
RUN_FULL_SCAN=1 python3 scanner/run_live_scan.py
python3 scripts/check-dashboard-shape.py
DEPLOY_PUSH=1 bash scripts/deploy-scanner-results.sh
```

If the scanner was already run:

```sh
cd /home/ubuntu/puc-trading
make validate
python3 scripts/check-dashboard-shape.py
DEPLOY_PUSH=1 bash scripts/deploy-scanner-results.sh
```

## 8. No-Push Dry Run

Default behavior does not push.

Run:

```sh
cd /home/ubuntu/puc-trading
bash scripts/deploy-scanner-results.sh
```

Expected ending:

```text
would push (DEPLOY_PUSH=1 to actually push)
```

If there is no changed scan result, expected ending:

```text
nothing to publish
```

## 9. Roll Back A Bad Publish

Rollback happens in the dashboard repo:

```sh
cd /home/ubuntu/pft-validator
git log --oneline -5
git revert <bad-commit-sha>
git push
```

After rollback, verify:

```sh
curl -s https://pft.permanentupperclass.com/scanner/scan-results.json | python3 -m json.tool >/dev/null
```

Then reload:

```text
https://pft.permanentupperclass.com/scanner/
```

## 10. Failure Recovery

Bad JSON:

- Stop cron if enabled.
- Revert the bad dashboard commit.
- Run `python3 scripts/check-dashboard-shape.py` against the local file.
- Run the scanner again if needed.
- Publish only after the shape check passes.

If the deploy script reports a secret-pattern hit:

- Do not push.
- Inspect the staged dashboard file.
- Remove the offending value from the generated output path.
- Rotate the credential if it was real.
- Re-run the deploy script.

The scanner output should never include keys, tokens, private URLs, broker
settings, or raw runtime logs.

If `RUN_FULL_SCAN=1` fails during scanner execution:

- Confirm IB Gateway is running.
- Confirm the scanner port matches the gateway port.
- Confirm delayed data is acceptable for the current scan.
- Run the scanner manually and inspect logs.

Do not switch to stale publish-only mode as a workaround.

If `make validate` fails in the private runtime:

- Inspect `~/puc-trading/corpus/convergence-latest.json`.
- Confirm `generated_at` is fresh.
- Confirm each score row has ticker, theme, score, tier, and status.
- Regenerate the convergence artifact.

Do not publish scan results generated from an invalid artifact.

If `check-dashboard-shape.py` fails:

- Read every printed missing field.
- Compare the scanner output with dashboard `index.html`.
- Update the scanner or dashboard together.
- Re-run the shape check.

The shape checker exists to prevent a silent dashboard break.

## 11. Git Hygiene

The deploy script stages only:

```text
scanner/scan-results.json
.gitignore
```

It must not run broad staging commands.

Local IB Gateway files are ignored:

```text
jts.ini
launcher.log
dgpdjeilgkccmlebkicghonjccocflnajmhbcnmh/
__pycache__/
.DS_Store
```

Do not delete those files as part of deploy.

## 12. Operator Notes

Keep the public dashboard boring:

- Fresh timestamp.
- Valid JSON.
- Clear failure when stale.
- No secrets.
- No private artifacts.
- No automatic execution.

The deploy path should be easy to audit from shell history and Git commit
history.
