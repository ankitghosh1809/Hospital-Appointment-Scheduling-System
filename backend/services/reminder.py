import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models.appointment import get_upcoming_appointments
from db import execute_query
from config import EMAIL_CONFIG


def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_CONFIG["user"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(EMAIL_CONFIG["host"], EMAIL_CONFIG["port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["user"], EMAIL_CONFIG["password"])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[Email Error] {e}")
        return False


def send_reminders():
    appointments = get_upcoming_appointments(hours_ahead=24)
    sent = 0
    for appt in (appointments or []):
        body = f"""Dear {appt['patient_name']},

Reminder: You have an appointment with {appt['doctor_name']} on {appt['appointment_date']} at {appt['appointment_time']}.

Please arrive 10 minutes early. Contact us to reschedule if needed.

Regards,
Hospital Appointment Team"""
        if send_email(appt["patient_email"], f"Appointment Reminder - {appt['appointment_date']}", body):
            execute_query(
                "INSERT INTO reminders (appointment_id, reminder_type) VALUES (%s, 'email')",
                (appt["appointment_id"],),
            )
            sent += 1
    return sent
