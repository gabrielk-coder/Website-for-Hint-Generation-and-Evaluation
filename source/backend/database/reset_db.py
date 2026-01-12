def reset_db_logic(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE hints, metrics, questions RESTART IDENTITY CASCADE;")
        conn.commit()
        cursor.close()
   
        conn.close()
    except Exception as e:
        print(f"Logic Error: {e}")
        raise e