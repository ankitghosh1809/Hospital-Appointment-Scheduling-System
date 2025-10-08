import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB Error] {e}")
        return None


def execute_query(query, params=None, fetch=False):
    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)
    result = None

    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid
    except Error as e:
        print(f"[Query Error] {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return result
