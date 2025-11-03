from db import execute_query


def book_appointment(patient_id, doctor_id, date, time, reason=None):
    if not is_slot_available(doctor_id, date, time):
        return None

    query = """
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason)
        VALUES (%s, %s, %s, %s, %s)
    """
    return execute_query(query, (patient_id, doctor_id, date, time, reason))


def is_slot_available(doctor_id, date, time):
    rows = execute_query(
        """
        SELECT COUNT(*) as cnt FROM appointments
        WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s
        AND status = 'scheduled'
        """,
        (doctor_id, date, time),
        fetch=True,
    )
    return rows[0]["cnt"] == 0 if rows else True


def cancel_appointment(appointment_id):
    execute_query(
        "UPDATE appointments SET status = 'cancelled' WHERE appointment_id = %s",
        (appointment_id,),
    )


def complete_appointment(appointment_id):
    execute_query(
        "UPDATE appointments SET status = 'completed' WHERE appointment_id = %s",
        (appointment_id,),
    )


def get_appointment_by_id(appointment_id):
    rows = execute_query(
        """
        SELECT a.*, p.name as patient_name, p.email as patient_email,
               d.name as doctor_name, d.specialization
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id = %s
        """,
        (appointment_id,),
        fetch=True,
    )
    return rows[0] if rows else None


def get_appointments_by_patient(patient_id):
    return execute_query(
        """
        SELECT a.*, d.name as doctor_name, d.specialization,
               py.status as payment_status, py.amount, py.payment_method
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        LEFT JOIN payments py ON a.appointment_id = py.appointment_id
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """,
        (patient_id,),
        fetch=True,
    )


def get_appointments_by_doctor_and_date(doctor_id, date):
    return execute_query(
        """
        SELECT a.*, p.name as patient_name, p.phone as patient_phone, p.email as patient_email
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.doctor_id = %s AND a.appointment_date = %s AND a.status = 'scheduled'
        ORDER BY a.appointment_time
        """,
        (doctor_id, date),
        fetch=True,
    )


def get_upcoming_appointments(hours_ahead=24):
    return execute_query(
        """
        SELECT a.*, p.name as patient_name, p.email as patient_email,
               d.name as doctor_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.status = 'scheduled'
          AND TIMESTAMP(a.appointment_date, a.appointment_time)
              BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL %s HOUR)
          AND a.appointment_id NOT IN (SELECT appointment_id FROM reminders)
        """,
        (hours_ahead,),
        fetch=True,
    )


def get_all_appointments():
    return execute_query(
        """
        SELECT a.*, p.name as patient_name, d.name as doctor_name, d.specialization,
               py.status as payment_status, py.amount
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        LEFT JOIN payments py ON a.appointment_id = py.appointment_id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        LIMIT 100
        """,
        fetch=True,
    )
