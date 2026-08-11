import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Reused across calls (and across warm serverless invocations) instead of
# opening a fresh TCP+TLS+auth connection to Neon on every single query.
_conn = None


def get_connection():
    global _conn
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Add it in Vercel → Settings → Environment Variables."
        )
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(DATABASE_URL)
    return _conn


def execute_query(query, params=None, fetch=False):
    global _conn
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        try:
            cur.execute(query, params or ())
        except psycopg2.OperationalError:
            # cached connection died between requests (e.g. Neon closed it
            # after being idle) - reconnect once and retry
            cur.close()
            _conn = psycopg2.connect(DATABASE_URL)
            conn = _conn
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(query, params or ())

        if fetch:
            result = [dict(r) for r in cur.fetchall()]
        else:
            conn.commit()
            # cur.description is None unless the statement had a RETURNING
            # clause (or was a SELECT). Calling fetchone() without one
            # raises psycopg2.ProgrammingError: no results to fetch.
            if cur.description is not None:
                row = cur.fetchone()
                result = list(row.values())[0] if row else None
            else:
                result = cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
    return result
