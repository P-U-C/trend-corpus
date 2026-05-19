#!/bin/bash
# refresh-convergence.sh
#
# Refresh ~/puc-trading/corpus/convergence-latest.json from the current
# state of trend-corpus + trend-intel-private. Runs the opportunity-
# generator for all 14 themes against the public corpus, merges each
# resulting opportunity-rows.json into convergence-latest.json, and
# (optionally) commits + pushes to puc-trading.
#
# Idempotent: re-running with no theme data changes is a no-op.
#
# Env:
#   DEPLOY_PUSH      1 = git push puc-trading after the merge (default 0)
#   TREND_CORPUS_DIR public corpus checkout (default ~/trend-corpus)
#   TREND_INTEL_DIR  private artifacts checkout (default ~/trend-intel-private)
#   PUC_TRADING_DIR  scanner-feed checkout (default ~/puc-trading)
#
# Output:
#   /tmp/refresh-convergence.log (per-theme generator output)
#   ${PUC_TRADING_DIR}/corpus/convergence-latest.json (the merged artifact)

set -euo pipefail

TREND_CORPUS_DIR="${TREND_CORPUS_DIR:-$HOME/trend-corpus}"
TREND_INTEL_DIR="${TREND_INTEL_DIR:-$HOME/trend-intel-private}"
PUC_TRADING_DIR="${PUC_TRADING_DIR:-$HOME/puc-trading}"

log() { printf "[%s] %s\n" "$(date -u +%FT%TZ)" "$*"; }

THEMES=(
    peptides
    ai-infrastructure
    quantum-computing
    nuclear-smr
    robotics-humanoid
    defense-ai
    space-satellite
    bitcoin-mining
    bci-neurotech
    solid-state-battery
    synthetic-biology
    edge-ai
    photonic-computing
    longevity
    # cicadas is a hand-authored operator macro thesis (see
    # puc-trading/trades/cicadas.md). It has no trend-corpus sector
    # theme dir, so generate_opportunities will skip it (no
    # opportunity-config.yaml under trends/cicadas/). The merge loop
    # below picks up the pre-placed
    # trend-intel-private/themes/cicadas/artifacts/opportunity-rows.json
    # so the cicadas ticker universe flows into convergence-latest.
    cicadas
)

# Refresh trend-corpus first so we pick up any aggregates pushed by runtime users.
log "git pull trend-corpus"
git -C "$TREND_CORPUS_DIR" pull --quiet --rebase || true

for theme in "${THEMES[@]}"; do
    theme_dir="$TREND_CORPUS_DIR/trends/$theme"
    if [ ! -d "$theme_dir" ]; then
        log "skip $theme: no theme directory"
        continue
    fi
    if [ ! -f "$theme_dir/opportunity-config.yaml" ]; then
        log "skip $theme: no opportunity-config.yaml"
        continue
    fi
    out_dir="$TREND_INTEL_DIR/themes/$theme/artifacts"
    mkdir -p "$out_dir"
    out_path="$out_dir/opportunity-rows.json"
    log "generate-opportunities $theme"
    python3 "$TREND_INTEL_DIR/scripts/generate_opportunities.py" \
        --theme "$theme" \
        --themes-dir "$TREND_CORPUS_DIR/trends" \
        --out "$out_path" 2>&1 | head -3
done

# Snapshot the existing convergence-latest.json so we can merge each theme
# additively. The merger's "llm-source" is treated as the existing baseline.
target="$PUC_TRADING_DIR/corpus/convergence-latest.json"
work="$(mktemp --suffix=.json)"
trap 'rm -f "$work"' EXIT
cp "$target" "$work"

# Normalize legacy snake_case theme_ids -> kebab-case (matches trend-corpus
# directory names). Without this, fixture-seeded rows like "ai_infrastructure"
# don't dedupe against new generator rows like "ai-infrastructure" and the
# scanner sees both as separate themes.
log "normalize theme_ids in baseline (snake -> kebab)"
python3 - "$work" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text())
norm_map = {
    "ai_infrastructure": "ai-infrastructure",
    "glp_1_peptides": "peptides",
    "quantum_computing": "quantum-computing",
    "nuclear_smr": "nuclear-smr",
    "robotics_humanoid": "robotics-humanoid",
    "defense_ai": "defense-ai",
    "space_satellite": "space-satellite",
    "bitcoin_mining": "bitcoin-mining",
    "bci_neurotech": "bci-neurotech",
    "solid_state_battery": "solid-state-battery",
    "synthetic_biology": "synthetic-biology",
    "edge_ai": "edge-ai",
    "photonic_computing": "photonic-computing",
}
def norm(tid):
    return norm_map.get(tid, tid)
for row in d.get("scores", []):
    if "theme_id" in row:
        row["theme_id"] = norm(row["theme_id"])
# Dedupe themes array on normalized id.
seen = {}
for t in d.get("themes", []):
    tid = norm(t.get("theme_id", ""))
    if not tid:
        continue
    t["theme_id"] = tid
    # Prefer the entry with the cleaner theme_name (no underscores) if dupes.
    if tid not in seen or "_" in (seen[tid].get("theme_name") or ""):
        seen[tid] = t
d["themes"] = list(seen.values())
p.write_text(json.dumps(d, indent=2, sort_keys=True))
PY

for theme in "${THEMES[@]}"; do
    opp="$TREND_INTEL_DIR/themes/$theme/artifacts/opportunity-rows.json"
    if [ ! -f "$opp" ]; then
        continue
    fi
    log "merge_convergence $theme"
    python3 "$PUC_TRADING_DIR/corpus/merge_convergence.py" \
        --llm-source "$work" \
        --opportunity-source "$opp" \
        --out "$work" >/dev/null
done

# Atomic publish.
mv "$work" "$target"
trap - EXIT

count_rows="$(python3 -c "import json; print(len(json.load(open('$target'))['scores']))")"
count_themes="$(python3 -c "import json; print(len(json.load(open('$target'))['themes']))")"
log "merged convergence-latest.json: scores=$count_rows themes=$count_themes"

if [ "${DEPLOY_PUSH:-0}" != "1" ]; then
    log "DEPLOY_PUSH=0 (default) -- not committing or pushing"
    exit 0
fi

cd "$PUC_TRADING_DIR"
git add -- corpus/convergence-latest.json
if git diff --cached --quiet; then
    log "no convergence-latest changes; skipping commit"
    exit 0
fi
git commit -m "convergence: refresh at $(date -u +%FT%TZ) scores=$count_rows themes=$count_themes"
git push origin HEAD:main
log "pushed convergence-latest"
