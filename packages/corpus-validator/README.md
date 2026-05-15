# corpus-validator

Local validator for `trend-corpus`.

It uses PyYAML when available and otherwise supports JSON input only. CI installs PyYAML and pytest as the only test dependencies.

Run from the repository root:

```sh
PYTHONPATH=packages/corpus-validator python3 -m corpus_validator validate .
```

