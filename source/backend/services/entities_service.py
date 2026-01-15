import json
from typing import Dict, List, Any

def get_entities_for_session(conn, session_id: str) -> Dict[int, List[Dict[str, Any]]]:
    results = {}
    
    try:
        query = """
        SELECT 
            e.hint_id,
            e.entity,
            e.ent_type,
            e.start_index,
            e.end_index,
            e.metadata_json
        FROM entities e
        JOIN hints h ON e.hint_id = h.id
        JOIN questions q ON h.question_id = q.id
        WHERE q.session_id = %s
        ORDER BY e.hint_id, e.start_index ASC
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (session_id,))
        rows = cursor.fetchall()
        
        for row in rows:
            h_id = row[0]
            entity_data = {
                "text": row[1],
                "type": row[2],
                "start": row[3],
                "end": row[4],
                "metadata": json.loads(row[5]) if row[5] else {}
            }
            
            if h_id not in results:
                results[h_id] = []
            results[h_id].append(entity_data)
            
        return results

    except Exception as e:
        print(f"[Entities Service Error]: {e}")
        return {}