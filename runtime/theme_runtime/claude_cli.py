"""
claude_cli.py - shared wrapper around the `claude` CLI.

Used by extract and packet. Separated so auth-detection lives in one
place.
"""
from __future__ import annotations

import subprocess


class AuthError(RuntimeError):
    """Raised when claude CLI says auth is expired / login required."""


_AUTH_MARKERS = (
    "login",
    "unauthorized",
    "authenticate",
    "token expired",
    "not logged in",
    "credentials",
    "oauth",
)


def run_claude(prompt_text: str, model: str = "sonnet", timeout: int = 300) -> str:
    """Invoke `claude -p` in print mode. Returns stdout as string.

    Raises AuthError if the CLI complains about credentials; RuntimeError on
    any other non-zero exit.
    """
    # Strip NUL bytes -- subprocess refuses arguments containing them.
    # Source content can legitimately leak NULs (binary PDFs, malformed
    # HTML, etc.) when the fetcher's Content-Type sniff doesn't catch
    # the case. Cheaper to sanitize at the boundary than at every fetch.
    if "\x00" in prompt_text:
        prompt_text = prompt_text.replace("\x00", "")
    result = subprocess.run(
        ["claude", "-p", prompt_text, "--model", model, "--output-format", "text"],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        stderr_lc = (result.stderr or "").lower()
        if any(m in stderr_lc for m in _AUTH_MARKERS):
            raise AuthError(
                "claude auth failed -- run 'claude' as this user to re-login: "
                + (result.stderr or "")[:300]
            )
        raise RuntimeError(
            f"claude CLI failed (exit {result.returncode}): "
            + (result.stderr or "")[:500]
        )
    return result.stdout
