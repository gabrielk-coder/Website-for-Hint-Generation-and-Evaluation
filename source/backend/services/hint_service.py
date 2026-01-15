import json
from datetime import datetime
from typing import List, Dict, Any
from .question_service import get_latest_question_id, clear_metrics_for_question
from sentence_transformers import SentenceTransformer


import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers.tokenization_utils_base")

# Initialize Model GLOBALLY
try:
    sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"Error loading SBERT model: {e}")
    sbert_model = None


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_hints_for_session(conn, session_id: str) -> List[Dict[str, Any]]:
    qid = get_latest_question_id(conn, session_id)
    if not qid:
        return []
    
    cur = conn.cursor()
    cur.execute("SELECT id, hint_text FROM hints WHERE question_id = %s ORDER BY id ASC", (qid,))
    return [{"hint_id": r[0], "hint_text": r[1]} for r in cur.fetchall()]

def save_hint(conn, session_id: str, hint_text: str) -> int:
    qid = get_latest_question_id(conn, session_id)
    if not qid:
        raise ValueError("No active question found for this session.")
    
    clear_metrics_for_question(conn, qid)
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM answers WHERE question_id = %s ORDER BY created_at DESC LIMIT 1",
        (qid,)
    )
    
    row = cur.fetchone() 

    if row is not None:
        answer_id = row[0]
        cur.execute(
            """
            INSERT INTO hints (question_id, hint_text, answer_id, created_at) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id
            """,
            (qid, hint_text, answer_id, _now())
        )
    else:
        cur.execute(
            """
            INSERT INTO hints (question_id, hint_text, created_at) 
            VALUES (%s, %s, %s) 
            RETURNING id
            """,
            (qid, hint_text, _now())
        )
        
    new_id = cur.fetchone()[0]
    conn.commit()

    return new_id

def update_hint(conn, hint_id: int, new_text: str) -> int:
    cur = conn.cursor()
    
    cur.execute("SELECT question_id FROM hints WHERE id = %s", (hint_id,))
    row = cur.fetchone()
    qid = row[0] if row else None

    cur.execute(
        "UPDATE hints SET hint_text = %s, updated_at = %s WHERE id = %s",
        (new_text, _now(), hint_id)
    )
    conn.commit()
    
    if qid:
        clear_metrics_for_question(conn, qid)
        
    return cur.rowcount

def delete_hint(conn, hint_id: int) -> int:
    cur = conn.cursor()
    
    cur.execute("SELECT question_id FROM hints WHERE id = %s", (hint_id,))
    row = cur.fetchone()
    qid = row[0] if row else None
    
    cur.execute("DELETE FROM hints WHERE id = %s", (hint_id,))
    conn.commit()
    
    if qid:
        clear_metrics_for_question(conn, qid)
        
    return cur.rowcount

def delete_all_hints(conn, session_id: str) -> None:
    qid = get_latest_question_id(conn, session_id)
    if qid:
        cur = conn.cursor()
        cur.execute("DELETE FROM hints WHERE question_id = %s", (qid,))
        conn.commit()
        clear_metrics_for_question(conn, qid)

def get_detailed_metrics(conn, session_id: str) -> List[Dict[str, Any]]:
    qid = get_latest_question_id(conn, session_id)
    if not qid:
        return []

    cur = conn.cursor()
    cur.execute("SELECT id, hint_text FROM hints WHERE question_id = %s ORDER BY id ASC", (qid,))
    hints = cur.fetchall()

    result = []

    for hid, text in hints:
        cur.execute("SELECT name, value FROM metrics WHERE hint_id = %s", (hid,))
        metrics = {row[0]: row[1] for row in cur.fetchall()}
        
        result.append({
            "id": hid,
            "text": text,
            "convergence": metrics.get("convergence"),
            "relevance": metrics.get("relevance"),
            "answer_leakage": metrics.get("answer-leakage"),
            "readability": metrics.get("readability"),
            "familiarity": metrics.get("familiarity"),
        })
    return result


def get_convergence_scores(conn, session_id: str) -> List[Dict[str, Any]]:
    qid = get_latest_question_id(conn, session_id)
    if not qid:
        return []

    cur = conn.cursor()

    cur.execute("SELECT id, hint_text FROM hints WHERE question_id = %s ORDER BY id ASC", (qid,))
    hints = cur.fetchall()

    result = []

    for hid, text in hints:
        cur.execute(
            "SELECT metadata_json FROM metrics WHERE hint_id = %s AND name = 'convergence'", 
            (hid,)
        )
        row = cur.fetchone()

        candidate_status = {}

        if row:
            metadata_str = row[0]
            try:
                meta_data = json.loads(metadata_str)
                if isinstance(meta_data, dict):
                    if "scores" in meta_data and isinstance(meta_data["scores"], dict):
                        candidate_status = meta_data["scores"]
                    else:
                        candidate_status = meta_data     
            except json.JSONDecodeError:
                candidate_status = {}
        result.append({
            "id": hid,
            "text": text,
            "candidates": candidate_status 
        })

    return result



def calculate_similarities_using_sbert(hints: List[str]) -> List[List[float]]:
    if not sbert_model: return []
    if not hints: return []
    embeddings = sbert_model.encode(hints, convert_to_tensor=True)
    similarities = sbert_model.similarity(embeddings, embeddings)
    return similarities.tolist()

def get_embedding_similarities(conn, session_id: str) -> List[List[float]]:
    qid = get_latest_question_id(conn, session_id)
    if not qid:
        return []

    cur = conn.cursor()
    cur.execute("SELECT hint_text FROM hints WHERE question_id = %s ORDER BY id ASC", (qid,))
    rows = cur.fetchall()
    
    if not rows:
        return []
        
    hint_texts = [r[0] for r in rows]
    return calculate_similarities_using_sbert(hint_texts)