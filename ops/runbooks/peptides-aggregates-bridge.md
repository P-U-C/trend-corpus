# Peptides Aggregates Bridge

How the live peptides runtime on `city-worker-301` publishes aggregate-only
public views into `trends/peptides/aggregates/`. The bridge keeps the
peptides theme alive in the public corpus without leaking the private
runtime's raw claim history, packet questions, or per-claim values.

## Boundary in one sentence

The exporter runs as user `peptide` on `city-worker-301`, queries the
private `db.sqlite` read-only, emits a single JSON file conforming to
`schemas/aggregates.schema.json`, and the pf-scout-bot box pulls that JSON
over scp and commits it into `~/trend-corpus/trends/peptides/aggregates/`.

## What gets published vs not

Same as `trends/peptides/aggregates/README.md`. Read that before changing
this runbook. The exporter MUST refuse to emit anything not on the allowlist.

## Components

```
city-worker-301 (private)                      pf-scout-bot (this box)
+------------------------------+               +-------------------------------+
| /home/peptide/peptide-corpus |               | ~/trend-corpus                |
|   db.sqlite (private)        |               |   trends/peptides/aggregates/ |
|   scripts/                   |               |     peptides-aggregates.json  |
|     export-public-aggregates |--- scp -->    |                               |
|       .py                    |               | scripts/sync-peptides-        |
|                              |               |   aggregates.sh (NEW)         |
| cron (peptide):              |               |                               |
|   weekly run of exporter     |               | cron (ubuntu):                |
|                              |               |   weekly pull + commit        |
+------------------------------+               +-------------------------------+
```

## Exporter contract

Located at `/home/ubuntu/peptide-corpus/scripts/export-public-aggregates.py`
on `city-worker-301` (reference implementation). The operator copies it to
`/home/peptide/peptide-corpus/scripts/` for production use (the live db
lives under `/home/peptide`, not `/home/ubuntu`).

Behavior:

- Reads `~/peptide-corpus/db.sqlite` read-only.
- Computes three rolling windows: 30, 90, 365 days, ending at `now`.
- For each window: `claims_total`, `claims_by_category` (counts), `top_entities`
  (slug + mentions), `top_peptides` (name + mentions).
- Suppresses any entity / peptide bucket with mention count below
  `--min-count` (default 3). Configurable.
- Emits `~/peptide-corpus/out/peptides-aggregates.json`. Overwrites the file
  in place; the file is the latest snapshot, not a history.
- Stdlib-only. No new pip dependencies.
- Exits 0 on success, non-zero on parse / IO error.
- Logs no raw claim text and no claim IDs.

The exporter must be safe to run as a cron job under user `peptide`.

## Install steps (operator)

1. Confirm the reference implementation runs cleanly:

   ```bash
   ssh city-worker-peptides
   python3 ~/peptide-corpus/scripts/export-public-aggregates.py --help
   python3 ~/peptide-corpus/scripts/export-public-aggregates.py --dry-run | head -30
   ```

2. Promote the script to the runtime user:

   ```bash
   sudo cp ~/peptide-corpus/scripts/export-public-aggregates.py \
           /home/peptide/peptide-corpus/scripts/
   sudo chown peptide:peptide /home/peptide/peptide-corpus/scripts/export-public-aggregates.py
   sudo chmod 755 /home/peptide/peptide-corpus/scripts/export-public-aggregates.py
   ```

3. Add to peptide's cron. Edit `/etc/cron.d/peptide-corpus` and append:

   ```
   # weekly aggregate export for the public trend-corpus theme
   0 6 * * 1  cd /home/peptide/peptide-corpus && python3 scripts/export-public-aggregates.py >> /var/log/peptide-aggregates.log 2>&1
   ```

   Mondays 06:00 UTC is recommended. Aggregate-shape doesn't move fast; a
   weekly cadence keeps git history readable.

4. Verify the output appears:

   ```bash
   sudo ls -la /home/peptide/peptide-corpus/out/peptides-aggregates.json
   sudo head /home/peptide/peptide-corpus/out/peptides-aggregates.json
   ```

## Cross-machine sync (this box)

Lives at `~/pf-scout-bot/deploy/sync-peptides-aggregates.sh` (to be written
as a follow-up; not yet committed). Behavior:

- scp `peptide@city-worker-peptides:~/peptide-corpus/out/peptides-aggregates.json`
  to `~/trend-corpus/trends/peptides/aggregates/peptides-aggregates.json`
- Run the trend-corpus secret-pattern scan on the new file.
- Validate the file against `schemas/aggregates.schema.json` (extend the
  validator -- or use a one-shot jsonschema check) before commit.
- If unchanged content (same sha256), exit 0 with "nothing to publish".
- Otherwise: `git add -- trends/peptides/aggregates/peptides-aggregates.json`,
  commit with a deterministic message, push only when `DEPLOY_PUSH=1`.

The pf-scout-bot box already has SSH access to `city-worker-peptides` via
`~/.ssh/city-worker` (config alias `city-worker-peptides`). However, that
key authenticates as user `ubuntu`, which cannot read `/home/peptide`. To
make the scp work, the operator must either:

A. Grant the ubuntu user read access to
   `/home/peptide/peptide-corpus/out/peptides-aggregates.json` (chmod
   o+r on the file and o+x on parent dirs), OR
B. Have the exporter on the host copy its output to a path readable by
   ubuntu (e.g. `/var/lib/peptide-public/peptides-aggregates.json`), with
   appropriate ownership.

Option B is recommended -- it keeps the rest of /home/peptide private and
gives a clear "public output" path. Update the exporter's output path
accordingly when wiring up the sync.

## Preflight before enabling the cron

- Aggregates file validates against `schemas/aggregates.schema.json`.
- Secret-pattern scan over the file finds zero hits.
- `min_count_threshold` is non-zero (default 3 is fine for peptides today).
- The `windows` block reports plausible non-zero counts (sanity check that
  the exporter is actually reading the live db, not an empty stub).
- The file contains no claim text -- a quick grep for sample claim phrasing
  comes up empty.

## Rollback

If a bad publish lands:

1. `cd ~/trend-corpus && git revert <commit-sha>`
2. `DEPLOY_PUSH=1 git push origin main`

The public site is github-pages-static so the rollback is effective as soon
as the revert is pushed.

## Open follow-ups

- Implement `~/pf-scout-bot/deploy/sync-peptides-aggregates.sh` (the
  cross-machine pull + commit script). Currently a stub in this runbook.
- Decide which side runs `jsonschema` validation against
  `aggregates.schema.json`. The current trend-corpus validator does not
  auto-pick up aggregates JSON; it only validates the seven standard object
  types. Either extend the validator to recognize `aggregates/` directories
  or run a one-shot jsonschema check in the sync script.
- Decide cadence for OTHER themes when they spin up. Peptides is weekly;
  faster sectors may want daily.
