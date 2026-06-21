"""Data access functions for translations (history storage).

Favorites feature has been removed.
"""

from __future__ import annotations

from database import get_db, row_to_dict


def add_history(
    original_text: str,
    translated_text: str,
    source_language: str,
    target_language: str,
    detected_language: str | None = None,
) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO history (
                original_text,
                translated_text,
                source_language,
                target_language,
                detected_language
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                original_text,
                translated_text,
                source_language,
                target_language,
                detected_language,
            ),
        )
        row = conn.execute(
            "SELECT * FROM history WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return row_to_dict(row)


def list_history(limit: int = 25) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM history ORDER BY created_at DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]

