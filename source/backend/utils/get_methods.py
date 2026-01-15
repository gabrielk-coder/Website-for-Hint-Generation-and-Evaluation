from typing import List, Dict, Optional
import sqlite3
from typing import Any

def get_hints_for_session(conn: sqlite3.Connection, session_id: str) -> List[Dict[str, Any]]:
    """
    Liefert alle Hints für die gegebene Session-ID,
    inkl. zugehöriger Frage.
    """
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            h.id           AS hint_id,
            h.hint_text    AS hint_text,
            h.created_at   AS hint_created_at,
            q.id           AS question_id,
            q.text         AS question_text,
            q.created_at   AS question_created_at
        FROM hints h
        JOIN questions q ON q.id = h.question_id
        WHERE q.session_id = ?
        ORDER BY h.created_at DESC;
        """,
        (session_id,),
    )
    rows = cur.fetchall()
    return [dict(row) for row in rows]


def get_hinteval_metrics_names(conn: sqlite3.Connection) -> List[str]:
    """
    Lies alle unterschiedlichen Metric-Namen aus der DB.
    Erwartet eine bestehende Connection (z.B. aus app.state.db).
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT name
        FROM metrics
        WHERE name IS NOT NULL
        ORDER BY name;
        """
    )
    rows = cur.fetchall()
    return [row[0] for row in rows]
