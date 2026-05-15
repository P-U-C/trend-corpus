# Peptides Runtime Inventory

Single source of truth for the live peptide-corpus runtime. Anywhere else
in the repo that references the host should defer to this doc.

## The machine is ONE host with three names

| Identifier | Where it appears | Notes |
|---|---|---|
| `city-worker-peptides` | SSH config alias on the orchestration box (`pf-scout-bot`) | The name to use in shell commands and runbooks. |
| `city-worker-301` | Hostname returned by `uname -n` / `hostname` on the machine itself | Visible in shell prompts. Same machine. |
| `192.168.1.21` | LAN IP | Reachable from the orchestration box on the same /24. |

These all point to the same Ubuntu host. Earlier docs occasionally used
the on-box hostname; treat that as the same machine.

## Access

- SSH from the orchestration box:
  ```
  ssh city-worker-peptides
  ```
- The orchestrator's key is `~/.ssh/city-worker` on the pf-scout-bot box.
  Authenticates as user `ubuntu` on the peptides host.
- The actual runtime user is `peptide`, separate from `ubuntu`. The
  ubuntu user CANNOT read `/home/peptide/` without sudo.

## Directory layout on the peptides host

| Path | Owner | Role |
|---|---|---|
| `/home/peptide/peptide-corpus/` | peptide:peptide | **LIVE RUNTIME.** Cron-driven. |
| `/home/peptide/peptide-corpus/db.sqlite` | peptide:peptide | Live claims database. NEVER copied off-host. |
| `/home/peptide/peptide-corpus/out/packets/` | peptide:peptide | Generated decision packets. Private. |
| `/home/peptide/.claude/` | peptide:peptide | OAuth credentials for the Claude Code CLI. Private. |
| `/home/ubuntu/peptide-corpus/` | ubuntu:ubuntu | **DEV CHECKOUT.** Empty stub db. Used for the orchestrator to stage new scripts. |
| `/home/ubuntu/peptide-corpus/scripts/export-public-aggregates.py` | ubuntu:ubuntu | Reference aggregate exporter. Operator promotes to `/home/peptide/peptide-corpus/scripts/` via sudo cp. |
| `/etc/cron.d/peptide-corpus` | root | Schedules ingest + extract under user `peptide`. |

## Cron

`/etc/cron.d/peptide-corpus` runs as user `peptide`:

```
HOME=/home/peptide
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
SHELL=/bin/bash

0  */6 * * * cd /home/peptide/peptide-corpus && bash cron-wrap.sh ingest ingest.py  >> /var/log/peptide-ingest.log 2>&1
15 */6 * * * cd /home/peptide/peptide-corpus && bash cron-wrap.sh extract extract.py >> /var/log/peptide-extract.log 2>&1
```

When the aggregate-bridge ships, append (operator action):

```
0  6 * * 1   cd /home/peptide/peptide-corpus && python3 scripts/export-public-aggregates.py >> /var/log/peptide-aggregates.log 2>&1
```

## Auth model

- Live runtime uses Claude Code CLI OAuth (Claude Pro / Max subscription).
  Credentials in `/home/peptide/.claude/`. NOT API key.
- The orchestrator's SSH key authenticates as `ubuntu`. Has no path to
  `/home/peptide/`. The exporter is therefore promoted manually with
  `sudo cp` (documented in `peptides-aggregates-bridge.md`).

## Public artifacts

The only file from this runtime that is allowed to leave the host is
`peptides-aggregates.json`, produced by the aggregate exporter and
conforming to `schemas/aggregates.schema.json`. Privacy boundary spelled
out in `trends/peptides/aggregates/README.md`.

## Cross-machine sync

Not yet wired. See `ops/runbooks/peptides-aggregates-bridge.md` for the
target architecture: peptides host writes a public-readable copy of
`peptides-aggregates.json`, the orchestration box pulls via scp,
validates against the aggregates schema, runs the secret-pattern scan,
commits to `trends/peptides/aggregates/`, pushes only when `DEPLOY_PUSH=1`.

## Companion docs

- `ops/runbooks/peptides-aggregates-bridge.md` -- bridge operational steps
- `trends/peptides/aggregates/README.md` -- privacy boundary
- `docs/peptide-example.md` -- walkthrough of the public theme
