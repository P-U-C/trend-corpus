"""
theme_runtime - composable runtime for a trend-corpus theme.

A theme runtime is a small SQLite + cron pipeline that:

  1. fetches sources listed in sources.txt -> sources table (ingest)
  2. extracts atomic claims via Claude Code OAuth -> claims table (extract)
  3. emits decision packets on demand (packet)
  4. pushes daily digests + alerts to Telegram (notify)

The peptide-corpus runtime was the prototype. This package generalizes it
so any theme (peptides, ai-infrastructure, quantum-computing, ...) gets
the same pipeline shape with a 5-line theme-config.yaml.

All scripts read a ThemeContext, never module-globals from a HERE
directory. That makes deployment a copy-and-config exercise rather than
a fork-and-modify exercise.
"""
from .context import ThemeContext, load_context

__all__ = ["ThemeContext", "load_context"]
__version__ = "0.1.0"
