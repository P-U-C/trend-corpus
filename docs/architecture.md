# Architecture

`trend-corpus` separates public research structure from private execution runtimes.

The public repo stores:

- Schemas for theme manifests and corpus objects.
- Taxonomy for claim categories, theme status, tiers, and execution states.
- Theme directories containing source, claim, entity, event, thesis, decision-packet, and watchlist objects.
- A validator that checks object shape, references, public safety rules, and secret patterns.

The runtime pattern comes from the peptides corpus:

1. Sources are collected from public pages.
2. Claims are extracted as append-only evidence records.
3. Claims can be superseded instead of rewritten.
4. Category half-lives determine freshness.
5. Decision packets combine claims and theses, but public trade-relevant packets remain human-reviewed.

Private systems consume generated files, not in-process public repo code. For `llm-convergence`, the intended seam is a versioned `convergence-latest.json` artifact with `ticker`, `theme`, `score`, `tier`, and `status` rows.

