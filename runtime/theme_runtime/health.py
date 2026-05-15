"""
health - verify the claude CLI auth + HOME are usable for this theme.

Returns an exit-style status code via the run() function:
  0 = all good
  1 = claude CLI missing or not executable
  2 = auth failed (login needed)
  3 = something else went wrong
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

from .context import ThemeContext


def run(ctx: ThemeContext) -> int:
    claude = shutil.which("claude")
    if not claude:
        print("FAIL: 'claude' not found on PATH", file=sys.stderr)
        return 1
    print(f"ok   claude CLI at: {claude}")
    home = os.environ.get("HOME")
    if not home:
        print("FAIL: $HOME is not set", file=sys.stderr)
        return 3
    print(f"ok   HOME={home}")
    cred_dir = os.path.join(home, ".claude")
    if os.path.isdir(cred_dir):
        print(f"ok   ~/.claude/ exists")
    else:
        print("WARN ~/.claude/ does not exist -- login may not have completed", file=sys.stderr)
    try:
        result = subprocess.run(
            ["claude", "-p", "Reply with exactly: auth ok", "--output-format", "text"],
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        print("FAIL: claude CLI timed out (60s)", file=sys.stderr)
        return 3
    if result.returncode != 0:
        err_lc = (result.stderr or "").lower()
        if any(
            m in err_lc
            for m in ("login", "unauthorized", "authenticate", "not logged in",
                      "credentials", "oauth", "token")
        ):
            print("FAIL: auth required -- run 'claude' as this user to log in.", file=sys.stderr)
            return 2
        print(f"FAIL: claude exited {result.returncode}", file=sys.stderr)
        return 3
    out = (result.stdout or "").strip()
    if "auth ok" not in out.lower():
        print(f"WARN: unexpected output: {out[:200]!r}", file=sys.stderr)
    else:
        print("ok   round-trip prompt succeeded")
    print(f"\nhealth({ctx.theme_id}): all checks passed")
    return 0
