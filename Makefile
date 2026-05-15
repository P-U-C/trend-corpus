PYTHON ?= python3
PYTHONPATH := packages/corpus-validator

.PHONY: validate test populate-convergence scan deploy-check up down

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
