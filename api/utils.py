import datetime


def to_jsonable(value):
    """
    Convert a raw DB value into something Flask's jsonify() can serialize.

    psycopg2 (PostgreSQL) returns TIME columns as datetime.time and
    TIMESTAMP/DATE columns as datetime.datetime/datetime.date. Neither
    is JSON-serializable on its own, so both need to become strings.
    (This differs from MySQL drivers, which return TIME columns as
    datetime.timedelta -- handled here too for safety.)
    """
    if isinstance(value, datetime.timedelta):
        total = int(value.total_seconds())
        return f"{total // 3600:02d}:{(total % 3600) // 60:02d}"
    if isinstance(value, datetime.time):
        total = value.hour * 3600 + value.minute * 60 + value.second
        return f"{total // 3600:02d}:{(total % 3600) // 60:02d}"
    if isinstance(value, (datetime.datetime, datetime.date)):
        return str(value)
    return value


def clean_row(row):
    """Apply to_jsonable to every value in a DB row (dict)."""
    return {k: to_jsonable(v) for k, v in row.items()}
