import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def execute_query(query, params=None, fetch=False):
    conn = get_connection()
    if not conn:
        return None
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    result = None
    try:
        cur.execute(query, params or ())
        if fetch:
            result = [dict(r) for r in cur.fetchall()]
        else:
            conn.commit()
            row = cur.fetchone()
            result = list(row.values())[0] if row else cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
    return result
