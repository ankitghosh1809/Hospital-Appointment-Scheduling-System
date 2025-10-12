from db import execute_query


def get_all_doctors():
    return execute_query("SELECT * FROM doctors ORDER BY specialization, name", fetch=True)


def get_doctor_by_id(doctor_id):
    rows = execute_query("SELECT * FROM doctors WHERE doctor_id = %s", (doctor_id,), fetch=True)
    return rows[0] if rows else None


def get_doctors_by_specialization(spec):
    return execute_query(
        "SELECT * FROM doctors WHERE specialization LIKE %s", (f"%{spec}%",), fetch=True
    )


def add_doctor(name, specialization, email, phone, avail_from="09:00:00", avail_to="17:00:00"):
    query = """
        INSERT INTO doctors (name, specialization, email, phone, available_from, available_to)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    return execute_query(query, (name, specialization, email, phone, avail_from, avail_to))
