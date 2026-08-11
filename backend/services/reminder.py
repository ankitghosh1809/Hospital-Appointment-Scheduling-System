import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models.appointment import get_upcoming_appointments, get_appointments_by_doctor_and_date
from models.doctor import get_all_doctors
from db import execute_query
from config import EMAIL_CONFIG, HOSPITAL_TZ
from utils import to_jsonable


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


def send_daily_doctor_summaries():
    """Email every doctor their own schedule for today. Meant to run once
    each morning (see the second cron line in the README)."""
    today = datetime.datetime.now(HOSPITAL_TZ).date().isoformat()
    doctors = get_all_doctors()
    sent = 0
    for doctor in (doctors or []):
        if not doctor.get("email"):
            continue

        appts = get_appointments_by_doctor_and_date(doctor["doctor_id"], today)
        if not appts:
            continue

        schedule_lines = "\n".join(
            f"  {to_jsonable(a['appointment_time'])} - {a['patient_name']}"
            f" ({a.get('patient_phone') or 'no phone on file'})"
            for a in appts
        )
        body = f"""Good morning {doctor['name']},

You have {len(appts)} appointment(s) scheduled today ({today}):

{schedule_lines}

Regards,
Hospital Appointment Team"""

        if send_email(doctor["email"], f"Today's Schedule - {today}", body):
            sent += 1
    return sent
