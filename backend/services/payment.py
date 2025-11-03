from db import execute_query


def create_payment(appointment_id, amount, method="cash"):
    return execute_query(
        "INSERT INTO payments (appointment_id, amount, payment_method, status) VALUES (%s, %s, %s, 'pending')",
        (appointment_id, amount, method),
    )


def mark_payment_paid(appointment_id, method="cash"):
    execute_query(
        "UPDATE payments SET status = 'paid', payment_method = %s WHERE appointment_id = %s",
        (method, appointment_id),
    )


def mark_payment_refunded(appointment_id):
    execute_query(
        "UPDATE payments SET status = 'refunded' WHERE appointment_id = %s",
        (appointment_id,),
    )


def get_payment_status(appointment_id):
    rows = execute_query(
        "SELECT * FROM payments WHERE appointment_id = %s", (appointment_id,), fetch=True
    )
    return rows[0] if rows else None


def get_pending_payments():
    return execute_query(
        """
        SELECT py.*, a.appointment_date, p.name as patient_name, d.name as doctor_name
        FROM payments py
        JOIN appointments a ON py.appointment_id = a.appointment_id
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE py.status = 'pending'
        ORDER BY a.appointment_date
        """,
        fetch=True,
    )
