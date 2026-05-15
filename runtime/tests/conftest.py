"""Shared pytest fixtures for theme_runtime tests."""
from __future__ import annotations

import sys
from pathlib import Path

# Make theme_runtime importable without installing
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
