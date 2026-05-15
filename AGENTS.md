# Agent Pattern

Claude acts as orchestrator: it reads the taxonomy, defines the sector research brief, reviews outputs, and makes the final call on what enters the corpus.

Codex acts as implementer: it creates files, normalizes objects, wires schemas, runs validation, and keeps repository changes small and auditable.

For new sectors, Claude and Codex may run independent research passes. Their outputs are aggregated and reviewed by a human or a third reviewer agent before becoming a theme.

Private runtimes stay behind file boundaries. Public corpus data may emit artifacts such as `convergence-latest.json`; scanners consume those artifacts without importing corpus-populator code or credentials.

Trade-relevant decisions must stop at `execution_state: human_review_required` in this public repo.

