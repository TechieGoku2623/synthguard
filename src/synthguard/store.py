"""DuckDB helpers for Phase 0 screen rows. Local files only."""

from __future__ import annotations

from pathlib import Path

import duckdb

from synthguard.schemas import ScreenResult


def write_screens(path: Path, rows: list[ScreenResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    con = duckdb.connect(str(path))
    try:
        con.execute(
            """
            CREATE TABLE screens (
                query_id VARCHAR,
                status VARCHAR,
                exit_code INTEGER,
                length INTEGER,
                max_identity DOUBLE,
                would_flag BOOLEAN,
                annotation VARCHAR
            )
            """
        )
        for row in rows:
            con.execute(
                "INSERT INTO screens VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    row.query_id,
                    row.status,
                    row.exit_code,
                    row.length,
                    row.max_identity,
                    row.would_flag_at_threshold,
                    row.annotation,
                ],
            )
    finally:
        con.close()


def count_screens(path: Path) -> int:
    con = duckdb.connect(str(path), read_only=True)
    try:
        result = con.execute("SELECT COUNT(*) FROM screens").fetchone()
        return int(result[0]) if result else 0
    finally:
        con.close()
