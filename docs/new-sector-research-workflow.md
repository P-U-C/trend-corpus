# Research Workflow

Claude orchestrates the sector spinup. It reads existing taxonomy, accepts a sector hint, defines the research questions, and reviews the final corpus objects.

Claude and Codex in research mode may independently identify sources, claims, entities, and open questions for the sector. The independent passes reduce single-agent bias and make disagreements visible.

Outputs are aggregated into a candidate theme. A human or third reviewer agent checks source quality, claim specificity, reference integrity, and whether the theme should exist.

After review, Codex implements the theme by copying `_template`, adding objects, and running validation. Trade-relevant outputs must gate at `human_review_required`; the public repo must never contain `approved_for_private_execution`.

Private scanners or dashboards consume generated artifacts through documented file seams. They do not import corpus-populator code or share credentials with this repo.

