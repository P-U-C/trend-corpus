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
|   `-- health.py                   # verify claude CLI auth
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

# 6. Cron
crontab -e
# add:
#   TRT_CONFIG=/home/ai-infra/ai-infra-corpus/theme-config.yaml
#   PYTHONPATH=/home/ai-infra/trend-corpus/runtime
#   HOME=/home/ai-infra
#   0  */6 * * * cd $HOME/ai-infra-corpus && bash $HOME/trend-corpus/runtime/templates/cron-wrap.sh ingest >> /var/log/ai-infra-ingest.log 2>&1
#   15 */6 * * * cd $HOME/ai-infra-corpus && bash $HOME/trend-corpus/runtime/templates/cron-wrap.sh extract --limit 50 >> /var/log/ai-infra-extract.log 2>&1
#   0  14 *  * * cd $HOME/ai-infra-corpus && bash $HOME/trend-corpus/runtime/templates/cron-wrap.sh notify digest >> /var/log/ai-infra-notify.log 2>&1
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
