PYTHON ?= python3
PYTHONPATH := packages/corpus-validator

.PHONY: validate test populate-convergence scan deploy-check up down new-theme validate-theme build-scanner-seed

validate:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m corpus_validator validate .

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest tests packages/corpus-validator/tests

populate-convergence:
	@echo "Public placeholder: the real convergence populator lives in the private ~/puc-trading runtime."
	@echo "Expected artifact contract: corpus/convergence-latest.json matching schemas/convergence.schema.json."

scan:
	@echo "Public placeholder: live options scanning is private and consumes validated corpus artifacts only."

deploy-check:
	@echo "Private dashboard shape check:"
	@echo "  cd ~/puc-trading && python3 scripts/check-dashboard-shape.py"
	@echo "This public target documents the command only; run it in the private runtime."

up:
	@echo "ops compose up placeholder"

down:
	@echo "ops compose down placeholder"

# Theme spin-up workflow. Replaces the bare "copy _template by hand" loop
# with a small set of named targets so each new sector follows the same
# shape. See docs/new-sector-research-workflow.md for the full pattern.

# Scaffold a new theme: copies trends/_template into trends/$(THEME) and
# rewrites the trend.yaml id/title. Refuses to overwrite an existing theme.
#   make new-theme THEME=quantum-computing
new-theme:
	@[ -n "$(THEME)" ] || (echo "usage: make new-theme THEME=<slug>"; exit 2)
	@[ ! -e trends/$(THEME) ] || (echo "trends/$(THEME) already exists"; exit 2)
	@cp -r trends/_template trends/$(THEME)
	@sed -i.bak \
		-e 's|^id: .*|id: $(THEME)|' \
		-e "s|^title: .*|title: $$(echo $(THEME) | sed -e 's|-| |g' -e 's|\b\(.\)|\u\1|g')|" \
		trends/$(THEME)/trend.yaml
	@rm -f trends/$(THEME)/trend.yaml.bak
	@echo "scaffolded trends/$(THEME) -- now edit trend.yaml, add sources/claims/entities/etc., then \`make validate-theme THEME=$(THEME)\`"

# Run the full validator scoped to a single theme. Useful when iterating on
# a sector without re-validating the whole repo each time. Falls back to
# repo-wide validate (the validator does not yet support per-theme scopes
# directly, but the output is filterable).
#   make validate-theme THEME=quantum-computing
validate-theme:
	@[ -n "$(THEME)" ] || (echo "usage: make validate-theme THEME=<slug>"; exit 2)
	@[ -d trends/$(THEME) ] || (echo "trends/$(THEME) does not exist"; exit 2)
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m corpus_validator validate . | grep -E "^trends/$(THEME)/|^validation passed" || true

# Emit the per-theme scanner-seed contract: the rows in convergence-latest.json
# the private scanner would consume for this theme. This is the bridge
# between a public theme's `sources/` and `entities/` and the M1 scanner
# artifact.
# Today: stub. Documents the contract; concrete generator lands in a
# follow-up that reads trends/$(THEME)/entities/*.yaml plus convergence
# scores and emits a JSON snippet conforming to schemas/convergence.schema.json.
#   make build-scanner-seed THEME=quantum-computing
build-scanner-seed:
	@[ -n "$(THEME)" ] || (echo "usage: make build-scanner-seed THEME=<slug>"; exit 2)
	@[ -d trends/$(THEME) ] || (echo "trends/$(THEME) does not exist"; exit 2)
	@echo "Scanner-seed contract for theme '$(THEME)':"
	@echo "  inputs:  trends/$(THEME)/entities/*.yaml (must include tickers[])"
	@echo "           trends/$(THEME)/trend.yaml (theme name = scanner join key)"
	@echo "  output:  JSON rows conforming to schemas/convergence.schema.json"
	@echo "           {ticker, theme_id, theme, score, tier, status, ...}"
	@echo "  consumer: ~/puc-trading/corpus/convergence-latest.json populator"
	@echo "(generator implementation pending; this target documents the contract)"
