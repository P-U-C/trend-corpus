# Metalayer API Placeholder

This directory sketches a future read-mostly web API for the metalayer.

Documented routes:

- `GET /themes` returns registered theme summaries.
- `GET /themes/<id>` returns one theme summary.
- `GET /convergence/latest` returns a private convergence artifact proxy response.
- `POST /questions` returns a decision-packet-shaped response and routes the question to a human-review queue.
- `GET /watchlists` returns watchlist summaries.

The stub does not read the real corpus or private runtime. It only proves the route shape.

POST endpoints never route to execution. They create or return review candidates with `execution_state: human_review_required`.

## Run

```sh
python3 app.py
```

Then visit:

```text
http://127.0.0.1:8080/themes
http://127.0.0.1:8080/watchlists
```

## Environment

No environment variables are required for the stub. See `.env.example` for names a real implementation would use.

