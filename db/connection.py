import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():

    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is missing from .env")

    try:
        return psycopg2.connect(database_url)
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        raise