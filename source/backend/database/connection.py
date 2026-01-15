import os
import psycopg2.pool
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend\.env")
print("Loaded .env for DB Connection", flush=True)
# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "hinteval_db")
DB_USER = os.getenv("DB_USER", "hinteval_user")
DB_PASS = os.getenv("DB_PASS", "secure_university_password")

pg_pool = None

def init_pool():
    global pg_pool
    print("Initializing PostgreSQL Connection Pool...", flush=True)
    try:
        pg_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        print("PostgreSQL initialized and Pool ready.", flush=True)
    except Exception as e:
        print(f"Error initializing DB Pool: {e}")

def close_pool():
    global pg_pool
    if pg_pool:
        pg_pool.closeall()
        print("DB Pool closed.", flush=True)

def get_db():
    """
    Dependency that provides a database connection from the pool.
    """
    global pg_pool
    if not pg_pool:
        raise HTTPException(500, "Database pool not initialized")
    
    conn = pg_pool.getconn()
    try:
        yield conn
    finally:
        pg_pool.putconn(conn)