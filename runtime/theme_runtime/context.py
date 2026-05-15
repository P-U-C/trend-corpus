"""
ThemeContext - the single config object every runtime function consumes.

Construction:
  ctx = load_context(path_to_theme_config_yaml)

The YAML schema is documented in templates/theme-config.example.yaml.
Missing optional fields get sensible defaults.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class ThemeContext:
    """All state every theme_runtime function needs.

    Required:
      theme_id: short slug, e.g. "peptides", "ai-infrastructure"
      theme_name: human-readable title
      root: directory containing db.sqlite, sources.txt, prompts/, out/

    Optional:
      extract_model: claude model alias for extract.py (default "sonnet")
      packet_model: claude model alias for packet.py (default "opus")
      source_text_cap: chars per source sent to Claude (default 30000)
      min_text_len: skip pages under this many chars (default 200)
      max_text_len: truncate pages above this many chars (default 80000)
      claim_categories: enum tuple for the claims.category column
      half_life_defaults: dict {category: int days}
      telegram_env_file: path to .env containing TG_BOT_TOKEN + TG_CHAT_ID
      telegram_bot_token: literal token (overrides env_file)
      telegram_chat_id: literal chat id (overrides env_file)
      message_prefix: short tag prepended to all Telegram notifications
                      (e.g. "[ai-infrastructure]")
    """

    theme_id: str
    theme_name: str
    root: Path

    extract_model: str = "sonnet"
    packet_model: str = "opus"
    source_text_cap: int = 30000
    min_text_len: int = 200
    max_text_len: int = 80000

    claim_categories: tuple[str, ...] = (
        "regulatory",
        "manufacturing",
        "market",
        "clinical",
        "pricing",
        "corporate",
    )
    half_life_defaults: dict[str, int] = field(
        default_factory=lambda: {
            "regulatory": 90,
            "pricing": 30,
            "corporate": 60,
            "manufacturing": 180,
            "market": 365,
            "clinical": 3650,
        }
    )

    telegram_env_file: Path | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    message_prefix: str = ""

    # Derived (filled in __post_init__)
    db_path: Path = field(init=False)
    sources_path: Path = field(init=False)
    prompts_dir: Path = field(init=False)
    out_dir: Path = field(init=False)
    packets_dir: Path = field(init=False)
    schema_path: Path = field(init=False)

    def __post_init__(self):
        self.root = Path(self.root).expanduser()
        self.db_path = self.root / "db.sqlite"
        self.sources_path = self.root / "sources.txt"
        self.prompts_dir = self.root / "prompts"
        self.out_dir = self.root / "out"
        self.packets_dir = self.out_dir / "packets"
        self.schema_path = self.root / "schema.sql"

    # ------ Telegram credential resolution ------

    def resolve_telegram(self) -> tuple[str | None, str | None]:
        """Return (token, chat_id), reading env or env_file as documented."""
        token = self.telegram_bot_token or os.environ.get("TG_BOT_TOKEN") or \
                os.environ.get("TELEGRAM_BOT_TOKEN")
        chat = self.telegram_chat_id or os.environ.get("TG_CHAT_ID") or \
               os.environ.get("TELEGRAM_CHAT_ID")
        if (not token or not chat) and self.telegram_env_file:
            env_path = Path(self.telegram_env_file).expanduser()
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key, _, val = line.partition("=")
                    val = val.strip().strip('"').strip("'")
                    if not val:
                        continue
                    if not token and key in {"TG_BOT_TOKEN", "TELEGRAM_BOT_TOKEN"}:
                        token = val
                    if not chat and key in {"TG_CHAT_ID", "TELEGRAM_CHAT_ID"}:
                        chat = val
        return token, chat


def load_context(config_path: str | os.PathLike) -> ThemeContext:
    """Load a theme-config.yaml and return a ThemeContext.

    The config keys (required: theme_id, theme_name, root) match the
    ThemeContext fields directly. Unknown keys are ignored. Missing
    optional keys use dataclass defaults.
    """
    if yaml is None:
        raise RuntimeError("PyYAML is required to load theme-config.yaml")
    path = Path(config_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"theme-config not found: {path}")
    data: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
    for required in ("theme_id", "theme_name", "root"):
        if required not in data:
            raise ValueError(f"theme-config missing required field: {required}")
    # Resolve `root` relative to the config file's directory if it's not absolute.
    root = Path(data["root"]).expanduser()
    if not root.is_absolute():
        root = (path.parent / root).resolve()
    kwargs = {
        "theme_id": data["theme_id"],
        "theme_name": data["theme_name"],
        "root": root,
    }
    for opt in (
        "extract_model", "packet_model",
        "source_text_cap", "min_text_len", "max_text_len",
        "message_prefix",
        "telegram_bot_token", "telegram_chat_id",
    ):
        if opt in data:
            kwargs[opt] = data[opt]
    if "telegram_env_file" in data:
        kwargs["telegram_env_file"] = Path(data["telegram_env_file"]).expanduser()
    if "claim_categories" in data:
        kwargs["claim_categories"] = tuple(data["claim_categories"])
    if "half_life_defaults" in data:
        kwargs["half_life_defaults"] = dict(data["half_life_defaults"])
    return ThemeContext(**kwargs)
