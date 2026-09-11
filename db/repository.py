import os
import psycopg2
from db.connection import get_db_connection

def init_db(schema_path: str="db/schema.sql") -> None:
    
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at {schema_path}")
    
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_db_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
        print("Tables initialized successfully.")

    except psycopg2.Error as e:
        print(f"Failed to execute schema migration: {e}")
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    init_db()