import psycopg2
import json
import csv
import io
import tempfile
import os
from datetime import datetime
from typing import Any, Dict, List
from hinteval import Dataset
from hinteval.cores import Subset, Instance
from .generation_service import generate_only_answer

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



def get_current_question_id(conn, session_id: str) -> int | None:
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM questions WHERE session_id = %s ORDER BY created_at DESC LIMIT 1", 
        (session_id,)
    )
    row = cur.fetchone()
    return row[0] if row else None

# ==========================================
# EXPORT LOGIC (Using hinteval)
# ==========================================

import psycopg2
import json
import tempfile
import os
from typing import Dict, Any
from hinteval import Dataset
from hinteval.cores import Subset, Instance

def export_session_json(conn, session_id: str, full_export: bool = True) -> Dict[str, Any]:
    qid = get_current_question_id(conn, session_id)
    if not qid:
        return {}

    with conn.cursor() as cur:
        cur.execute("SELECT text FROM questions WHERE id = %s", (qid,))
        row = cur.fetchone()
        question_text = row[0] if row else ""

        cur.execute("SELECT answer_text FROM answers WHERE question_id = %s LIMIT 1", (qid,))
        ans_row = cur.fetchone()
        answers_list = [ans_row[0]] if ans_row else []

        cur.execute("SELECT id, hint_text FROM hints WHERE question_id = %s ORDER BY id ASC", (qid,))
        hint_rows = cur.fetchall()
        hints_text_list = [h[1] for h in hint_rows]

        dataset = Dataset(name=f"session_{session_id}")
        subset = Subset(name="export")
        instance = Instance.from_strings(
            question=question_text,
            answers=answers_list,
            hints=hints_text_list
        )
        subset.add_instance(instance, q_id=str(qid))
        dataset.add_subset(subset)

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp:
            temp_path = tmp.name
        
        try:
            dataset.store_json(temp_path)
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        if full_export:
            try:
                target_instance = data['subsets']['export']['instances'][str(qid)]
            except KeyError:
                return data

            cur.execute("""
                SELECT candidate_text, is_eliminated, created_at 
                FROM candidate_answers 
                WHERE question_id = %s
            """, (qid,))
            
            candidates_data = []
            for c_row in cur.fetchall():
                candidates_data.append({
                    "text": c_row[0],
                    "is_eliminated": bool(c_row[1]),
                    "created_at": str(c_row[2])
                })
            
            if candidates_data:
                target_instance['candidates_full'] = candidates_data
                target_instance['candidates'] = [c['text'] for c in candidates_data]

            json_hints = target_instance.get('hints', [])
            metrics_by_id = {}

            if len(json_hints) == len(hint_rows):
                for i, (db_hint_id, db_hint_text) in enumerate(hint_rows):
                    h_obj = json_hints[i]
                    h_obj['id'] = db_hint_id

                    cur.execute("""
                        SELECT name, value, metadata_json 
                        FROM metrics 
                        WHERE hint_id = %s
                    """, (db_hint_id,))
                    
                    metric_rows = cur.fetchall()
                    metrics_dict = {}
                    
                    if metric_rows:
                        h_obj['metrics'] = []
                        for m_name, m_val, m_meta in metric_rows:
                            m_entry = {
                                "name": m_name, 
                                "value": m_val,
                                "metadata": json.loads(m_meta) if m_meta else None
                            }
                            h_obj['metrics'].append(m_entry)
                            metrics_dict[m_name] = m_val

                        metrics_by_id[str(db_hint_id)] = metrics_dict

                    try:
                        cur.execute("""
                            SELECT entity, ent_type, start_index, end_index, metadata_json 
                            FROM entities 
                            WHERE hint_id = %s
                        """, (db_hint_id,))
                        
                        ent_rows = cur.fetchall()
                        if ent_rows:
                            h_obj['entities'] = []
                            for e_text, e_type, e_start, e_end, e_meta in ent_rows:
                                h_obj['entities'].append({
                                    "text": e_text,
                                    "type": e_type,
                                    "start": e_start,
                                    "end": e_end,
                                    "metadata": json.loads(e_meta) if e_meta else None
                                })
                    except psycopg2.Error:
                        conn.rollback()

                target_instance['hints'] = json_hints
                
                if metrics_by_id:
                    target_instance['metricsById'] = metrics_by_id

        return data

def export_session_csv_stream(conn, session_id: str):
    data_dict = export_session_json(conn, session_id, full_export=False)
    
  
    try:
        subsets = data_dict.get('subsets', {})
        export_subset = subsets.get('export', {})
        instances = export_subset.get('instances', {})
        first_key = next(iter(instances))
        instance_data = instances[first_key]
        
        q_text = instance_data.get('question', {}).get('question', '')
        a_text = instance_data.get('answers', [])[0].get('answer', '') if instance_data.get('answers') else ""
        hints = [h.get('hint', '') for h in instance_data.get('hints', [])]
        
    except (StopIteration, AttributeError, KeyError):
        q_text = ""
        a_text = ""
        hints = []

    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["type", "content"])
    if q_text:
        writer.writerow(["question", q_text])
    if a_text:
        writer.writerow(["answer", a_text])
    for h in hints:
        writer.writerow(["hint", h])
        
    output.seek(0)
    return output

# ==========================================
# IMPORT LOGIC (Using hinteval)
# ==========================================

def clear_session_data(conn, session_id: str):
    cur = conn.cursor()
    cur.execute("DELETE FROM questions WHERE session_id = %s", (session_id,))
    conn.commit()

def insert_imported_data(conn, session_id: str, data: Dict[str, Any]):
    """
    Parses a hinteval-compliant dictionary (re-serialized to file for loading)
    and inserts it into the database.
    """
    cur = conn.cursor()

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp:
        json.dump(data, tmp)
        temp_path = tmp.name

    try:
 
        dataset = Dataset.load_json(temp_path)
        

        instances = []
        for subset_name in dataset.subsets:
            subset = dataset.subsets[subset_name]
            instances.extend(subset.get_instances())
            
        if not instances:
            raise ValueError("No instances found in the imported Hinteval dataset.")

        inserted_count = 0
        
        for inst in instances:
       
            q_text = inst.question.question if hasattr(inst.question, 'question') else str(inst.question)
            
            cur.execute(
                "INSERT INTO questions (text, session_id, created_at) VALUES (%s, %s, %s) RETURNING id",
                (q_text, session_id, _now())
            )
            question_id = cur.fetchone()[0]

            ans_text = ""
            if inst.answers and len(inst.answers) > 0:
                first_ans = inst.answers[0]
                ans_text = first_ans.answer if hasattr(first_ans, 'answer') else str(first_ans)
            
            answer_id = None
            if ans_text:
                cur.execute(
                    "INSERT INTO answers (question_id, answer_text, created_at) VALUES (%s, %s, %s) RETURNING id",
                    (question_id, ans_text, _now())
                )
                answer_id = cur.fetchone()[0]
            else:
                print(f"Import: Answer missing for QID {question_id}, generating...", flush=True)
                model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
                ans_text = generate_only_answer(conn, q_text, model, question_id=question_id)
                cur.execute("SELECT id FROM answers WHERE question_id = %s ORDER BY id DESC LIMIT 1", (question_id,))
                answer_id = cur.fetchone()[0]

            for h_obj in inst.hints:
                h_text = h_obj.hint if hasattr(h_obj, 'hint') else str(h_obj)
                
                if h_text and h_text.strip():
                    cur.execute(
                        "INSERT INTO hints (question_id, answer_id, hint_text, created_at) VALUES (%s, %s, %s, %s)",
                        (question_id, answer_id, h_text.strip(), _now())
                    )
                    
            inserted_count += 1

        conn.commit()
        return {
            "info": f"Successfully imported {inserted_count} question(s) from Hinteval dataset.",
            "generated_answer": None 
        }

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def parse_csv_to_dict(content_bytes: bytes) -> Dict[str, Any]:
    text_stream = io.StringIO(content_bytes.decode('utf-8'))
    reader = csv.DictReader(text_stream)
    
    if reader.fieldnames:
        reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]

  
    q_text = ""
    a_text = ""
    hints = []
    
    for row in reader:
        r_type = row.get("type", "").strip().lower()
        content = row.get("content", "").strip()
        if not content: continue

        if r_type == "question":
            q_text = content
        elif r_type == "answer":
            a_text = content
        elif r_type == "hint":
            hints.append({"hint": content})

    instance_obj = {
        "question": {"question": q_text},
        "answers": [{"answer": a_text}] if a_text else [],
        "hints": hints
    }
    
    return {
        "subsets": {
            "csv_import": {
                "instances": {
                    "imported_1": instance_obj
                }
            }
        }
    }



from datetime import datetime
from typing import Dict, Any
import json


def load_full_preset_state(conn, session_id: str, data: Dict[str, Any]):
    """
    Inserts a full pre-computed state (Q, A, Hints, Candidates, Metrics) 
    into the database. It relies on DB to generate IDs and maintains relationships.
    """
    cur = conn.cursor()
    
    
    try:
        cur.execute(
            """
            INSERT INTO questions (text, session_id, created_at) 
            VALUES (%s, %s, %s) 
            RETURNING id
            """, 
            (data['question'], session_id, _now())
        )
        qid = cur.fetchone()[0]
        
        cur.execute(
            """
            INSERT INTO answers (question_id, answer_text, created_at) 
            VALUES (%s, %s, %s) 
            RETURNING id
            """, 
            (qid, data['groundTruth'], _now())
        )
        aid = cur.fetchone()[0]

        for h in data.get('hints', []):
            cur.execute(
                """
                INSERT INTO hints (question_id, answer_id, hint_text, created_at) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id
                """,
                (qid, aid, h['hint_text'], _now())
            )
            real_hint_id = cur.fetchone()[0]
            
            preset_local_id = str(h.get('hint_id')) 
            metrics_dict = data.get('metricsById', {}).get(preset_local_id, {})
            
            for metric_name, metric_value in metrics_dict.items():
                if metric_value is not None:
                    cur.execute(
                        """
                        INSERT INTO metrics (hint_id, name, value) 
                        VALUES (%s, %s, %s)
                        """, 
                        (real_hint_id, metric_name, float(metric_value))
                    )

        candidates = data.get('candidates', [])
        for c_text in candidates:
            cur.execute(
                """
                INSERT INTO candidate_answers (question_id, candidate_text, is_eliminated, created_at) 
                VALUES (%s, %s, %s, %s)
                """,
                (qid, c_text, 0, _now()) 
            )

        conn.commit()
        return {"status": "success", "question_id": qid}

    except Exception as e:
        conn.rollback()
        print(f"Error loading preset: {e}")
        raise e
    finally:
        cur.close()