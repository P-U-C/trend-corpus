# LLM Convergence

The `llm-convergence` theme documents a method for measuring whether consumer LLMs converge on the same ticker names for a sector theme.

The core thesis is a flow funnel: when multiple mainstream models recommend or mention the same small set of public tickers for the same theme, those tickers can become a concentrated attention target for retail investors.

The public corpus captures the method, claims, and validation hooks. The private scanner remains segregated and reads a generated `convergence-latest.json` artifact. The scanner-side join key is the theme name, and each row must include `ticker`, `theme`, `score`, `tier`, and `status`.

The included decision packet does not authorize execution. It asks whether a private scanner should consume a daily generated artifact once a populator exists, and it is gated with `execution_state: human_review_required`.

