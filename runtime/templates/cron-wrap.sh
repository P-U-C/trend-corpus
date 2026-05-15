#!/usr/bin/env bash
# cron-wrap.sh -- wrap a theme_runtime step, alert Telegram on failure.
#
# Usage from cron:
#   cron-wrap.sh ingest          # runs `python3 -m theme_runtime ingest`
#   cron-wrap.sh extract --limit 50
#   cron-wrap.sh health
#   cron-wrap.sh notify digest
#
# The first arg is a short label used in the alert message. The rest are
# theme_runtime subcommand + args.
#
# Requires TRT_CONFIG to point at a theme-config.yaml (set in cron env or
# this script's parent shell).

set -uo pipefail

LABEL="$1"
shift

TMP_ERR=$(mktemp)
python3 -m theme_runtime "$LABEL" "$@" 2> >(tee "$TMP_ERR" >&2)
EXIT=$?

if [[ $EXIT -ne 0 ]]; then
  ERR_TAIL=$(tail -c 500 "$TMP_ERR" 2>/dev/null || echo "(no stderr captured)")
  python3 -m theme_runtime notify alert "${LABEL} exit=${EXIT}"$'\n'"---stderr tail---"$'\n'"${ERR_TAIL}" || true
fi

rm -f "$TMP_ERR"
exit $EXIT
