# theme_runtime

Composable runtime for a trend-corpus theme. A theme runtime is a small
SQLite + cron pipeline that fetches sources, extracts atomic claims via
the Claude Code CLI, emits decision packets on demand, and pushes daily
digests to Telegram.

The peptide-corpus runtime was the prototype. This package generalizes
it: a 5-line `theme-config.yaml` is enough to spin up the same pipeline
for any sector.

## Layout

```
runtime/
|-- theme_runtime/                  <-- the Python package (this is what cron runs)
|   |-- __init__.py
|   |-- __main__.py                 # python3 -m theme_runtime <command>
|   |-- context.py                  # ThemeContext + load_context()
|   |-- db.py                       # schema + connect + migrate
|   |-- claude_cli.py               # claude CLI subprocess wrapper
|   |-- ingest.py                   # sources.txt -> sources table
|   |-- extract.py                  # sources -> claims via claude -p
|   |-- packet.py                   # question -> decision packet via claude -p
|   |-- status.py                   # quick corpus health
|   |-- notify.py                   # Telegram alerts / digests / packet pings
|   |-- health.py                   # verify claude CLI auth
|   |-- sync.py                     # pull sources + prompts from a trend-corpus checkout
|   `-- discover_entities.py        # flag claim slugs not in trend-corpus + draft entity YAMLs
|
|-- templates/
|   |-- theme-config.example.yaml   # copy + edit for each new theme
|   `-- cron-wrap.sh                # wraps a step + alerts on failure
|
|-- bin/
|   `-- trend-runtime               # short shim that delegates to `python3 -m theme_runtime`
|
`-- tests/
    `-- test_*.py
```

## Commands

The full lifecycle a theme runtime goes through, exposed as
`python3 -m theme_runtime --config <cfg> <command>`:

| Command | What it does | Calls Claude? | Runs on cron? |
|---|---|---|---|
| `init` | Create db.sqlite + dirs + empty sources.txt | no | no -- one-shot setup |
| `migrate` | Rename legacy `peptides` column to `topics` (idempotent) | no | no -- one-shot setup |
| `health` | Verify the claude CLI is logged in for this user | yes (tiny) | once after deploy |
| `sync --from <trend-corpus>` | Rebuild sources.txt + prompts from a public-theme checkout | no | yes -- daily 05:00 UTC |
| `ingest` | Fetch sources.txt URLs into the sources table | no | yes -- every 6h |
| `extract --limit N` | Run unprocessed sources through Claude -> claims | yes (1 per source) | yes -- 15min after each ingest |
| `packet "question"` | Generate a Decision Packet from active claims | yes (1) | no -- on demand or weekly |
| `status` | Print corpus health (sources/claims/packets counts) | no | no -- ad hoc |
| `recent -n N` | Show the N most-recent active claims | no | no -- ad hoc |
| `notify alert "msg"` | Send a one-line Telegram alert | no | wrapper-only (cron-wrap on failure) |
| `notify digest` | Send a 24h Telegram digest | no | yes -- daily 14:00 UTC |
| `notify packet <path>` | Telegram-ping that a new packet landed | no | called by packet.py end-of-run |
| `discover-entities --from <trend-corpus> [--notify]` | Find claim slugs not in `trends/<theme>/entities/`; draft entity YAMLs | yes (1 batch) | yes -- weekly Sunday 06:00 UTC |

The two most recent additions -- `sync` and `discover-entities` --
close the loop between the live runtime and the public template:

- **`sync`** keeps the host's `sources.txt` and `prompts/*.md` in lockstep
  with `trend-corpus/trends/<theme>/`. You edit the theme in the public
  repo + push; within 24h the cron pulls + rebuilds the host files
  atomically. No manual scp / ssh copy. The command is read-only on
  Claude (zero API cost) and idempotent (no-op when nothing changed).

- **`discover-entities`** closes the new-ticker gap: when claims tag a
  company slug that doesn't exist as an entity in `trend-corpus/trends/
  <theme>/entities/`, the weekly pass batches all unknowns into one
  Claude prompt, gets back JSONL of `{slug, tradable, ticker, exchange,
  entity_type, role, confidence}`, and drafts entity YAMLs at
  `/tmp/trt-discover/<theme>/ent_<slug>.yaml` for operator review. The
  `--notify` flag pings the operator's Telegram channel with the draft
  count + review path. Nothing is auto-merged; the operator commits
  keepers to trend-corpus, and the next daily `sync` propagates them
  back to the host.

## How a new theme spins up

Per-theme work is mechanical: edit a YAML, drop in a sources.txt + three
prompts (mirroring `trends/<theme>/docs/prompts.md`), point cron at a
single config path.

```bash
# On the runtime host (run as the theme's user, e.g. `ai-infra`):

sudo useradd -m -s /bin/bash ai-infra
sudo -iu ai-infra

# 1. Get the runtime code
git clone https://github.com/P-U-C/trend-corpus.git
export PYTHONPATH=$HOME/trend-corpus/runtime:$PYTHONPATH

# 2. Make the theme dir
mkdir -p ~/ai-infra-corpus/prompts
cd ~/ai-infra-corpus

# 3. Drop in config + sources + prompts (copy from trend-corpus/trends/ai-infrastructure/)
cp ~/trend-corpus/runtime/templates/theme-config.example.yaml theme-config.yaml
# edit theme-config.yaml: theme_id, theme_name, telegram_env_file, message_prefix
cp ~/trend-corpus/trends/ai-infrastructure/docs/prompts.md prompts/   # split into extract.md / packet.md / validate.md
# build sources.txt from trends/ai-infrastructure/sources/*.yaml (url field of each)

# 4. Initialize
export TRT_CONFIG=$PWD/theme-config.yaml
python3 -m theme_runtime init
python3 -m theme_runtime health   # verifies claude CLI is logged in

# 5. Telegram credentials
echo 'TG_BOT_TOKEN=...' > ~/.theme-runtime.env
echo 'TG_CHAT_ID=...' >> ~/.theme-runtime.env
chmod 600 ~/.theme-runtime.env

# 6. Cron -- five entries that cover the full closed loop
# (operator installs /etc/cron.d/ai-infra-corpus root-owned, or per-user crontab)
#
# Required env in the file/crontab:
#   TRT_CONFIG=/home/ai-infra/ai-infra-corpus/theme-config.yaml
#   PYTHONPATH=/home/ai-infra/trend-corpus-runtime
#   HOME=/home/ai-infra
#   PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
#
# Daily sync (pulls trend-corpus, rebuilds sources.txt + prompts/)
#   0  5 * * * ai-infra cd $HOME/trend-corpus && git pull --quiet 2>/dev/null; cd $HOME/ai-infra-corpus && bash $HOME/trend-corpus-runtime/templates/cron-wrap.sh sync --from $HOME/trend-corpus >> $HOME/logs/ai-infra-sync.log 2>&1
#
# Ingest every 6h
#   0  */6 * * * ai-infra cd $HOME/ai-infra-corpus && bash $HOME/trend-corpus-runtime/templates/cron-wrap.sh ingest >> $HOME/logs/ai-infra-ingest.log 2>&1
#
# Extract 15min after each ingest
#   15 */6 * * * ai-infra cd $HOME/ai-infra-corpus && bash $HOME/trend-corpus-runtime/templates/cron-wrap.sh extract --limit 50 >> $HOME/logs/ai-infra-extract.log 2>&1
#
# Daily digest at 14:00 UTC
#   0  14 * * * ai-infra cd $HOME/ai-infra-corpus && bash $HOME/trend-corpus-runtime/templates/cron-wrap.sh notify digest >> $HOME/logs/ai-infra-notify.log 2>&1
#
# Weekly entity discovery (Sunday 06:00 UTC; notifies operator if any drafts produced)
#   0  6 * * 0 ai-infra cd $HOME/ai-infra-corpus && bash $HOME/trend-corpus-runtime/templates/cron-wrap.sh discover-entities --from $HOME/trend-corpus --notify >> $HOME/logs/ai-infra-discover.log 2>&1
```

## Composability boundaries

- **Per-theme config** lives in `theme-config.yaml`. Reading it costs
  nothing -- the runtime only reads files declared in the config.
- **The runtime package** is pure Python stdlib + pyyaml + the `claude`
  CLI in PATH. No pip install required beyond pyyaml.
- **Prompts** are per-theme (different sector vocabulary). The runtime
  treats them as data files at `prompts/{extract,packet,validate}.md`.
- **Schema** is shared across themes. The `topics` column is the
  generic version of the prototype's `peptides` column.
- **Telegram** is per-theme via `message_prefix` (the same chat receives
  notifications from many themes, prefixed to disambiguate).

## Migrating an existing peptide-corpus runtime

```bash
# On the existing peptide host, as user `peptide`:
cd ~/peptide-corpus

# Pull the new runtime package next to your existing scripts:
git clone https://github.com/P-U-C/trend-corpus.git ~/trend-corpus
export PYTHONPATH=$HOME/trend-corpus/runtime:$PYTHONPATH

# Rename the legacy peptides column to topics (idempotent, safe):
TRT_CONFIG=$PWD/theme-config.yaml python3 -m theme_runtime migrate

# Write theme-config.yaml (theme_id: peptides, theme_name: Peptides, root: $PWD)
# and from this point you can replace the old standalone scripts with the
# generic ones:
#   python3 -m theme_runtime ingest      replaces  python3 ingest.py
#   python3 -m theme_runtime extract     replaces  python3 extract.py
#   python3 -m theme_runtime packet "Q"  replaces  python3 packet.py "Q"
# Update /etc/cron.d/peptide-corpus to call cron-wrap.sh instead of the
# standalone scripts. The standalone scripts can stay around as a
# fallback until you trust the migration.
```

## Tests

```bash
cd ~/trend-corpus/runtime
python3 -m pytest tests
```

The tests exercise the package against an in-memory sqlite + a fake
prompt directory; the claude CLI is mocked. No network, no Claude
credentials needed to run them.

## Companion repos

- `P-U-C/trend-corpus` -- this repo. Public template + schemas + theme
  manifests.
- `P-U-C/trend-intel-private` -- semi-private rich mirror that consumes
  the runtime's output and emits scanner-seed rows.
- `P-U-C/puc-trading` -- private. Reads merged convergence and runs the
  options scanner.
