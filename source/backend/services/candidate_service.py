import psycopg2
from datetime import datetime
from typing import List, Optional
from .question_service import get_latest_question_id, clear_metrics_for_question
from .generation_service import generate_only_candidates

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_candidates(conn, session_id: str) -> List[str]:
    qid = get_latest_question_id(conn, session_id)
    if not qid:
        return []
    
    cur = conn.cursor()
    cur.execute("SELECT candidate_text FROM candidate_answers WHERE question_id = %s ORDER BY id ASC", (qid,))
    return [r[0] for r in cur.fetchall()]

def save_candidate(conn, session_id: str, text: str, index: Optional[int] = None) -> None:
    qid = get_latest_question_id(conn, session_id)
    if not qid:
        raise ValueError("No active question found.")
    
    cur = conn.cursor()
    
    if index is None:
        cur.execute(
            "INSERT INTO candidate_answers (question_id, candidate_text, created_at) VALUES (%s, %s, %s)",
            (qid, text, _now())
        )
    else:
        cur.execute("SELECT id FROM candidate_answers WHERE question_id = %s ORDER BY id ASC", (qid,))
        rows = cur.fetchall()
        if index < 0 or index >= len(rows):
            raise IndexError("Candidate index out of range")
        
        cand_id = rows[index][0]
        cur.execute("UPDATE candidate_answers SET candidate_text = %s, updated_at = %s WHERE id = %s", (text,_now(),cand_id))
    
    conn.commit()
    clear_metrics_for_question(conn, qid)

def delete_candidate(conn, session_id: str, index: int) -> None:
    qid = get_latest_question_id(conn, session_id)
    if not qid:
        return
        
    cur = conn.cursor()
    cur.execute("SELECT id FROM candidate_answers WHERE question_id = %s ORDER BY id ASC", (qid,))
    rows = cur.fetchall()
    
    if index < 0 or index >= len(rows):
        raise IndexError("Candidate index out of range")
        
    cand_id = rows[index][0]
    cur.execute("DELETE FROM candidate_answers WHERE id = %s", (cand_id,))
    conn.commit()
    clear_metrics_for_question(conn, qid)

def delete_all_candidates(conn, session_id: str) -> None:
    qid = get_latest_question_id(conn, session_id)
    if qid:
        cur = conn.cursor()
        cur.execute("DELETE FROM candidate_answers WHERE question_id = %s", (qid,))
        conn.commit()
        clear_metrics_for_question(conn, qid)

def generate_candidates_for_session(
    conn, 
    session_id: str, 
    num_candidates: int,
    model_name: str,
    temperature: float,
    max_tokens: int,
    hints: Optional[List[str]] = None
) -> List[str]:
    """Generates and saves candidates for the current session."""
    qid = get_latest_question_id(conn, session_id)
    if not qid:
        raise ValueError("No active question to generate candidates for.")
        
    cur = conn.cursor()
    cur.execute("SELECT text FROM questions WHERE id = %s", (qid,))
    question = cur.fetchone()[0]
    
    candidates = generate_only_candidates(question, num_candidates, temperature, model_name, max_tokens,hints=hints)
    
    for c in candidates:
        cur.execute(
            "INSERT INTO candidate_answers (question_id, candidate_text, created_at) VALUES (%s, %s, %s)",
            (qid, c, _now())
        )
    conn.commit()
    clear_metrics_for_question(conn, qid)
    
    return candidates