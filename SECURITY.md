# Security

This public repo must never contain credentials, tokens, private keys, OAuth session files, private runtime databases, broker configuration, webhooks, chat IDs, private decision packets, personal trade context, or unreleased private claims.

Rotate any credential immediately if it is exposed in a commit, issue, log, artifact, or pull request.

Enable push protection and secret scanning in GitHub repository settings before publication.

The validator scans corpus content for these patterns. The policy file and validator source are excluded from self-matching because they document the patterns:

```text
OPENAI_API_KEY
ANTHROPIC_API_KEY
GITHUB_TOKEN
TELEGRAM_BOT_TOKEN
AWS_(ACCESS_KEY_ID|SECRET_ACCESS_KEY)
IBKR
PRIVATE_KEY
MNEMONIC
ghp_[A-Za-z0-9_]{20,}
github_pat_[A-Za-z0-9_]{20,}
sk-[A-Za-z0-9]{20,}
xox[baprs]-[A-Za-z0-9-]{10,}
-----BEGIN (RSA|OPENSSH|EC|DSA|PGP) PRIVATE KEY-----
(?i)(api[_-]?key|secret|token)\s*[:=]\s*['"][^'"]+['"]
```

