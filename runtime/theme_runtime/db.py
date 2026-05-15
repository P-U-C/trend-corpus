"""
db.py - sqlite helpers + schema initialization for a theme runtime.

The schema is theme-agnostic. Topics (the third lowercased-slug array on
each claim) used to be `peptides` in the prototype; renamed for general use.
Old peptide-corpus dbs can be migrated with `migrate_legacy_peptides_db()`.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
  id          INTEGER PRIMARY KEY,
  url         TEXT UNIQUE NOT NULL,
  fetched_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  raw_text    TEXT,
  processed   INTEGER DEFAULT 0,
  error       TEXT
);

CREATE INDEX IF NOT EXISTS idx_sources_unprocessed
  ON sources(processed) WHERE processed = 0;

CREATE TABLE IF NOT EXISTS claims (
  id                INTEGER PRIMARY KEY,
  source_id         INTEGER REFERENCES sources(id),
  claim             TEXT NOT NULL,
  category          TEXT,
  entities          TEXT,
  topics            TEXT,
  date_of_evidence  DATE,
  half_life_days    INTEGER DEFAULT 90,
  confidence        REAL DEFAULT 0.7 CHECK(confidence BETWEEN 0 AND 1),
  superseded_by     INTEGER REFERENCES claims(id),
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_claims_active_by_cat
  ON claims(category, date_of_evidence DESC) WHERE superseded_by IS NULL;

CREATE INDEX IF NOT EXISTS idx_claims_active_recent
  ON claims(date_of_evidence DESC) WHERE superseded_by IS NULL;

CREATE TABLE IF NOT EXISTS packets (
  id           INTEGER PRIMARY KEY,
  question     TEXT NOT NULL,
  verdict      TEXT,
  packet_path  TEXT,
  created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW IF NOT EXISTS fresh_claims AS
SELECT
  c.id, c.claim, c.category, c.entities, c.topics,
  c.date_of_evidence, c.confidence, c.half_life_days,
  s.url AS source_url
FROM claims c
LEFT JOIN sources s ON s.id = c.source_id
WHERE c.superseded_by IS NULL
  AND date(c.date_of_evidence, '+' || c.half_life_days || ' days') > date('now');
"""


def connect(db_path: Path) -> sqlite3.Connection:
    """Open a sqlite3 connection with WAL + FK on."""
    db_path = Path(db_path).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_schema(db_path: Path) -> None:
    """Create tables + indexes + view if they don't exist."""
    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def migrate_legacy_peptides_db(db_path: Path) -> bool:
    """Rename the legacy `peptides` column to `topics` if present.

    Returns True if a migration ran, False if no migration was needed.
    Idempotent. Safe to call against an already-migrated db.
    """
    conn = connect(db_path)
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(claims)").fetchall()]
        if "peptides" in cols and "topics" not in cols:
            conn.execute("ALTER TABLE claims RENAME COLUMN peptides TO topics")
            # Recreate the view since column renames don't propagate
            conn.execute("DROP VIEW IF EXISTS fresh_claims")
            conn.executescript(SCHEMA_SQL)
            conn.commit()
            return True
        return False
    finally:
        conn.close()
