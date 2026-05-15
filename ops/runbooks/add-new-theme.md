# Add New Theme Runbook

This is the operational version of the agent-spinup workflow.

Use it when adding a new sector to `trend-corpus`.

## 1. Define The Sector

Choose an ASCII slug:

```text
nuclear-smr
ai-infra
space-satellite
```

The slug becomes:

- The directory under `trends/`.
- The `id` in `trend.yaml`.
- A join key for future artifacts.

Avoid marketing labels that will drift quickly.

## 2. Run Independent Research Passes

Ask Claude orchestrator and Codex research-mode to independently enumerate:

- 8 to 15 upstream sources.
- Likely claim categories.
- Core entities.
- Relevant events.
- Known controversies or invalidation paths.
- Potential watchlist fields.

Research-mode is the slow, expensive pass. Use it to discover the sector shape, not to refresh routine claims.

## 3. Reconcile Outputs

Aggregate both outputs.

A third agent or human reviewer should:

- Drop weak or circular sources.
- Prefer primary sources where available.
- Normalize company, regulator, and product names.
- Identify 3 to 5 starter claims.
- Decide whether the theme is `emerging`, `growing`, `peak_hype`, or `post_peak`.

Document unresolved questions in the theme README.

## 4. Copy The Template

From the repo root:

```sh
cp -R trends/_template trends/<theme-slug>
```

Edit:

```text
trends/<theme-slug>/README.md
trends/<theme-slug>/trend.yaml
```

The `trend.yaml` object folder map should usually stay unchanged.

## 5. Add Sources

Create source objects in:

```text
trends/<theme-slug>/sources/
```

Source IDs must start with `src_`.

Prefer:

- Regulators.
- Company investor relations pages.
- SEC filings or equivalent public filings.
- Standards bodies.
- Reputable trade press.
- Public dashboards or datasets.

Do not add private runtime files or personal notes.

## 6. Define Entity Slugs

Create entity objects only when they help resolve claims.

Entity IDs must start with `ent_`.

Use stable slugs for:

- Companies.
- Regulators.
- Products.
- Technologies.
- Supply-chain nodes.

## 7. Write Starter Claims

Write 3 to 5 example claims in:

```text
trends/<theme-slug>/claims/
```

Claim IDs must start with `clm_`.

Each claim should include:

- A specific claim statement.
- A category.
- One or more source IDs.
- Evidence date.
- Confidence.

Keep claims narrow. Broad theses belong in `theses/`.

## 8. Write One Thesis

Create one thesis in:

```text
trends/<theme-slug>/theses/
```

Thesis IDs must start with `ths_`.

The thesis should combine the starter claims into an interpretable view.

## 9. Write One Decision Packet

Create one decision packet in:

```text
trends/<theme-slug>/decision-packets/
```

Decision packet IDs must start with `dp_`.

Required fields:

- `question`
- `verdict`
- `execution_state`
- `supporting_theses`
- `invalidation_conditions`

Trade-relevant packets must use `human_review_required`.

Never place private approval state in public corpus objects.

## 10. Add A Watchlist

Create one watchlist in:

```text
trends/<theme-slug>/watchlists/
```

Watchlist IDs must start with `wl_`.

Use `monitor_for` to list observable fields, such as:

- Status transitions.
- New source events.
- Rank changes.
- Freshness decay.
- Confidence changes.

## 11. Validate

Run:

```sh
make validate
make test
```

Fix all schema, reference, and safety errors before opening a PR.

## 12. Open A PR

The PR should include:

- Theme summary.
- Source list.
- Starter claims.
- Validation output.
- Known gaps.
- Any reviewer questions.

Keep the PR focused on one theme.

## 13. Register With The Metalayer

After the PR is accepted, register the new theme with the private metalayer runtime.

The metalayer should initially treat the theme as `research_only` or `watchlist_candidate` unless a human reviewer explicitly promotes it.

