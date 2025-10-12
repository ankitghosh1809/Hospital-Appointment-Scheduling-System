from db import execute_query


def add_patient(name, email, phone, dob=None, address=None):
    query = """
        INSERT INTO patients (name, email, phone, date_of_birth, address)
        VALUES (%s, %s, %s, %s, %s)
    """
    return execute_query(query, (name, email, phone, dob, address))


def get_patient_by_email(email):
    rows = execute_query("SELECT * FROM patients WHERE email = %s", (email,), fetch=True)
    return rows[0] if rows else None


def get_patient_by_id(patient_id):
    rows = execute_query("SELECT * FROM patients WHERE patient_id = %s", (patient_id,), fetch=True)
    return rows[0] if rows else None


def get_all_patients():
    return execute_query("SELECT * FROM patients ORDER BY name", fetch=True)
