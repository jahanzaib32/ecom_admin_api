# app/core/db.py
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from . import config # from app.core import config

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        # In a real app, you might raise a custom exception or handle this more gracefully
        raise ConnectionError(f"Database connection failed: {e}") # Raise for FastAPI to catch

@contextmanager
def db_cursor(commit: bool = False):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None: # Check if connection failed in get_db_connection
             raise ConnectionError("Failed to establish database connection.")
        cursor = conn.cursor(dictionary=True) # dictionary=True returns rows as dicts
        yield cursor
        if commit:
            conn.commit()
    except Error as e:
        if conn and conn.is_connected():
            conn.rollback()
        print(f"Database error: {e}")
        raise # Re-raise the exception to be handled by FastAPI or calling function
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()