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

## Composition

```
[private corpus populator]   ->   convergence-latest.json   ->   [private scanner runtime]
                                  (file seam, M1 contract)         (~/puc-trading/scanner/run_live_scan.py
                                                                     read-only brokerage, local-only)
                                                                          |
                                                                          v
                                                                  scan-results.json
                                                                  (M5 deploy contract)
                                                                          |
                                                                          v
                                                              [public scanner artifact]
                                                              (P-U-C/pft-validator/scanner/scan-results.json
                                                               static-served file)
                                                                          |
                                                                          v
                                                                 [public dashboard]
                                                            pft.permanentupperclass.com/scanner/
                                                            (static HTML, single fetch() of the artifact)
```

Note: the scanner is NOT a public component. The scanner RUNTIME is
private; only the scanner's OUTPUT ARTIFACT is published. No public
interface accepts queries; the dashboard reads a static file. There is
no `place_order`, `order_type`, `limit_price`, `stop_price`,
`account_id`, or other trade-action field anywhere in the publishable
chain. The validator in this repo enforces that those fields cannot
appear in any public corpus object.

For the peptides theme there is a parallel composition for the
aggregate-only bridge:

```
[live peptide-corpus runtime]   ->   [public-readable aggregate JSON]   ->   [public theme aggregates]
   /home/peptide on the                  /var/lib/peptide-public/                trends/peptides/aggregates/
   peptides host                         peptides-aggregates.json                peptides-aggregates.json
   (cron, claims db,                     (write-only by exporter,                (validated against
   packets -- all private)               read by ubuntu user for scp)            schemas/aggregates.schema.json,
                                                                                 secret-scanned,
                                                                                 committed by deploy script)
```

The aggregate path NEVER includes claim text, packet questions,
per-claim confidence, or supersedence relationships. See
`trends/peptides/aggregates/README.md` for the allowlist and
`ops/inventory/peptides-runtime.md` for the host topology.

