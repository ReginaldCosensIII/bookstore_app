import psycopg2
import os

def get_db_connection():
    """
    Establish and return a connection to the PostgreSQL database
    using the DATABASE_URL environment variable.
    """
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set.")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        raise
