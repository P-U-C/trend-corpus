#!/usr/bin/env python3
"""Ask one model one question, from whichever subscription is healthy.

Why this is not just `subprocess.run(["claude", ...])`
------------------------------------------------------
Both corpus stages ask a model a single, bounded question -- "find five recent
sources" and "say what this page establishes". Nothing about either is tied to
a vendor. But the cost is, and by a wide margin. Measured 2026-08-26 on
identical inputs, same source, same prompt:

    promote one source     claude -p   46,124 tokens     pfterminal  18,171
    discover one theme     claude -p  ~1,900,000         pfterminal  79,261

The discovery gap is not a model difference, it is a harness difference: the
Claude Code preamble is ~39k tokens re-read on every turn, and an agentic
search loop re-reads its own accumulated results on top of that. Corbanu's
`exec` answers the same question in one shot with `tools.web_search`.

The second reason matters more than the first: these are two different
subscriptions. Chad's Claude sub and his ChatGPT sub have separate limits, and
the failure he actually feels is a five-hour window emptied while he slept.
Being able to move a job between pools is the lever; being able to fall back
automatically is what stops the move from becoming a new single point of
failure.

The auth footgun, and why fallback is not optional
--------------------------------------------------
Corbanu shares ONE `~/.pfterminal/auth.json` with the always-on Telegram
connector, and two processes refreshing that OAuth token at once produces
"unauthorized / refresh token already used". Adding cron jobs makes a third
consumer. So a pfterminal failure here is expected occasionally and must not
cost a day of corpus: on any non-zero exit or empty answer, this falls through
to `claude -p` and the run continues.

Neither path is trusted blindly downstream. Every discovered URL is fetched and
title-checked before it is written, and every claim lands `review_state:
pending`. That verification net is what makes the choice of engine a cost
question rather than a quality risk.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "trend-corpus"
LEDGER = Path.home() / "logs" / "model-usage.jsonl"

_TOKENS = re.compile(r"tokens used\s*[\r\n]*\s*([\d,]+)")
AUTH_MARKERS = ("authenticate", "oauth", "revoked", "401", "login",
                "refresh token", "unauthorized")


class AuthFailure(RuntimeError):
    """Both engines refused us. Stop; do not write a day of empty results."""


def _record(stage: str, engine: str, tokens: int, seconds: float, ok: bool) -> None:
    """Append one line to the usage ledger.

    Moving work onto the ChatGPT subscription only helps if someone can see
    what it now costs there. `token-burn.py` reads Claude transcripts and is
    blind to this pool, so without a ledger the fix would trade a measured
    problem for an unmeasured one -- which is the failure this whole system
    keeps relearning.
    """
    try:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with LEDGER.open("a") as fh:
            fh.write(json.dumps({
                "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "stage": stage, "engine": engine, "tokens": tokens,
                "seconds": round(seconds, 1), "ok": ok,
            }) + "\n")
    except OSError:
        pass


def _pfterminal(prompt: str, *, web: bool, effort: str, timeout: int) -> tuple[str, int]:
    cmd = ["pfterminal", "exec", "--ephemeral", "--skip-git-repo-check",
           "-C", str(ROOT), "-c", f'model_reasoning_effort="{effort}"']
    if web:
        cmd += ["-c", "tools.web_search=true"]
    with tempfile.NamedTemporaryFile("r", suffix=".txt", delete=False) as fh:
        out_path = fh.name
    try:
        cmd += ["-o", out_path, prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        answer = Path(out_path).read_text(errors="replace").strip()
    finally:
        try:
            os.unlink(out_path)
        except OSError:
            pass
    m = _TOKENS.search(result.stderr or "")
    tokens = int(m.group(1).replace(",", "")) if m else 0
    if result.returncode != 0 or not answer:
        detail = ((result.stderr or "") + (result.stdout or "")).lower()
        raise RuntimeError("pfterminal: " + (
            "auth" if any(k in detail for k in AUTH_MARKERS)
            else f"exit {result.returncode}, {len(answer)} chars"))
    return answer, tokens


def _claude(prompt: str, *, web: bool, model: str, timeout: int) -> str:
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "text"]
    # With no tool needed, close the door: a model that decides to "check"
    # something anyway puts three turns back where one belongs.
    cmd += (["--allowed-tools", "WebSearch", "WebFetch"] if web
            else ["--disallowed-tools", "WebFetch", "WebSearch"])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        blob = ((result.stdout or "") + " " + (result.stderr or "")).lower()
        if any(k in blob for k in AUTH_MARKERS):
            raise AuthFailure(
                "claude auth failed — this run would find nothing and report "
                "success. Fix the login first.")
        raise RuntimeError((result.stderr or result.stdout or "")[:300])
    return result.stdout


def ask(prompt: str, *, stage: str, web: bool = False, engine: str = "auto",
        effort: str = "low", claude_model: str = "sonnet",
        timeout: int = 300) -> str:
    """One question, one answer. `engine` is auto | pfterminal | claude."""
    started = time.time()
    if engine in ("auto", "pfterminal"):
        try:
            answer, tokens = _pfterminal(prompt, web=web, effort=effort,
                                         timeout=timeout)
            _record(stage, "pfterminal", tokens, time.time() - started, True)
            return answer
        except (subprocess.TimeoutExpired, RuntimeError) as exc:
            _record(stage, "pfterminal", 0, time.time() - started, False)
            if engine == "pfterminal":
                raise
            print(f"  pfterminal unavailable ({exc}); falling back to claude",
                  flush=True)

    started = time.time()
    try:
        answer = _claude(prompt, web=web, model=claude_model, timeout=timeout)
    except Exception:
        _record(stage, "claude", 0, time.time() - started, False)
        raise
    _record(stage, "claude", 0, time.time() - started, True)
    return answer
