"""Tests for schema init + legacy peptides->topics migration."""
from __future__ import annotations

import sqlite3

from theme_runtime.db import SCHEMA_SQL, init_schema, migrate_legacy_peptides_db


def test_init_schema_creates_tables_and_view(tmp_path):
    db_path = tmp_path / "db.sqlite"
    init_schema(db_path)
    conn = sqlite3.connect(str(db_path))
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    views = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='view'"
    ).fetchall()}
    cols = {r[1] for r in conn.execute("PRAGMA table_info(claims)").fetchall()}
    assert tables == {"sources", "claims", "packets"}
    assert "fresh_claims" in views
    assert "topics" in cols
    assert "peptides" not in cols  # new schema is generic
    conn.close()


def test_init_schema_is_idempotent(tmp_path):
    db_path = tmp_path / "db.sqlite"
    init_schema(db_path)
    init_schema(db_path)  # second call must not error
    conn = sqlite3.connect(str(db_path))
    assert conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0] == 0
    conn.close()


def test_migrate_legacy_peptides_db(tmp_path):
    """Hand-build a legacy peptide-corpus db, then migrate it."""
    db_path = tmp_path / "legacy.sqlite"
    legacy_schema = """
    CREATE TABLE sources (
      id INTEGER PRIMARY KEY, url TEXT UNIQUE NOT NULL,
      fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      raw_text TEXT, processed INTEGER DEFAULT 0, error TEXT
    );
    CREATE TABLE claims (
      id INTEGER PRIMARY KEY, source_id INTEGER,
      claim TEXT NOT NULL, category TEXT,
      entities TEXT, peptides TEXT,
      date_of_evidence DATE, half_life_days INTEGER DEFAULT 90,
      confidence REAL DEFAULT 0.7,
      superseded_by INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE packets (
      id INTEGER PRIMARY KEY, question TEXT NOT NULL,
      verdict TEXT, packet_path TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    conn = sqlite3.connect(str(db_path))
    conn.executescript(legacy_schema)
    conn.execute("""
      INSERT INTO claims (claim, category, entities, peptides, date_of_evidence)
      VALUES ('test claim', 'regulatory', '["fda"]', '["semaglutide"]', '2026-05-01')
    """)
    conn.commit()
    conn.close()

    ran = migrate_legacy_peptides_db(db_path)
    assert ran is True

    conn = sqlite3.connect(str(db_path))
    cols = {r[1] for r in conn.execute("PRAGMA table_info(claims)").fetchall()}
    assert "topics" in cols
    assert "peptides" not in cols
    # Data preserved under the new column name
    rows = conn.execute("SELECT topics FROM claims").fetchall()
    assert rows[0][0] == '["semaglutide"]'
    conn.close()

    # Second call is a no-op
    assert migrate_legacy_peptides_db(db_path) is False
