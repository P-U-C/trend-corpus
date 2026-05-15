# Theme Authoring

Start a new sector by copying `trends/_template`:

```sh
cp -R trends/_template trends/my-sector
```

Use an ASCII slug for the directory and `trend.yaml` id.

Required steps:

1. Fill in `trend.yaml` with `id`, `title`, `status`, `schema_version`, and the `objects` folder map.
2. Add source objects first. Prefer primary sources and stable URLs.
3. Add claim objects with category, confidence, source references, and evidence date.
4. Add entities and events only when they help resolve claims.
5. Add theses that combine claims into an interpretable view.
6. Add decision packets only when they include non-empty invalidation conditions and `execution_state: human_review_required` for trade-relevant material.
7. Add watchlists for monitoring, not execution.
8. Run `make validate` and `make test`.

Object ID prefixes are stable: `src_`, `clm_`, `ent_`, `evt_`, `ths_`, `dp_`, and `wl_`.

