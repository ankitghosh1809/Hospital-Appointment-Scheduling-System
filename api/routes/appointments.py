import datetime
from flask import Blueprint, jsonify, request
from models.appointment import (
    book_appointment,
    cancel_appointment,
    complete_appointment,
    get_appointment_by_id,
    get_all_appointments,
    get_appointments_by_doctor_and_date,
)
from models.patient import get_patient_by_email, add_patient
from services.payment import create_payment
from config import DEFAULT_FEE

appointments_bp = Blueprint("appointments", __name__)


def clean(row):
    result = {}
    for k, v in row.items():
        if isinstance(v, (datetime.date, datetime.datetime)):
            result[k] = str(v)
        elif hasattr(v, "total_seconds"):
            total = int(v.total_seconds())
            result[k] = f"{total // 3600:02d}:{(total % 3600) // 60:02d}"
        else:
            result[k] = v
    return result


@appointments_bp.route("/", methods=["GET"])
def list_appointments():
    appts = get_all_appointments()
    return jsonify([clean(a) for a in (appts or [])])


@appointments_bp.route("/", methods=["POST"])
def create_appointment():
    data = request.get_json()

    required = ["email", "name", "doctor_id", "date", "time"]
    if not all(k in data for k in required):
        return jsonify({"error": f"Required fields: {', '.join(required)}"}), 400

    # get or create patient
    patient = get_patient_by_email(data["email"])
    if not patient:
        patient_id = add_patient(
            data["name"],
            data["email"],
            data.get("phone"),
            data.get("date_of_birth"),
            data.get("address"),
        )
        if not patient_id:
            return jsonify({"error": "Failed to register patient"}), 500
    else:
        patient_id = patient["patient_id"]

    time_val = data["time"] if len(data["time"]) == 8 else data["time"] + ":00"

    appointment_id = book_appointment(
        patient_id,
        data["doctor_id"],
        data["date"],
        time_val,
        data.get("reason"),
    )

    if not appointment_id:
        return jsonify({"error": "Slot already booked. Please pick another time."}), 409

    create_payment(appointment_id, DEFAULT_FEE)

    return jsonify({
        "appointment_id": appointment_id,
        "patient_id": patient_id,
        "message": "Appointment booked successfully",
        "fee": DEFAULT_FEE,
    }), 201


@appointments_bp.route("/<int:appointment_id>", methods=["GET"])
def get_appointment(appointment_id):
    appt = get_appointment_by_id(appointment_id)
    if not appt:
        return jsonify({"error": "Appointment not found"}), 404
    return jsonify(clean(appt))


@appointments_bp.route("/<int:appointment_id>/cancel", methods=["PATCH"])
def cancel(appointment_id):
    appt = get_appointment_by_id(appointment_id)
    if not appt:
        return jsonify({"error": "Appointment not found"}), 404
    if appt["status"] == "cancelled":
        return jsonify({"error": "Already cancelled"}), 400

    cancel_appointment(appointment_id)
    return jsonify({"message": "Appointment cancelled"})


@appointments_bp.route("/<int:appointment_id>/complete", methods=["PATCH"])
def complete(appointment_id):
    complete_appointment(appointment_id)
    return jsonify({"message": "Marked as completed"})


@appointments_bp.route("/doctor/<int:doctor_id>/date/<date>", methods=["GET"])
def doctor_day_schedule(doctor_id, date):
    appts = get_appointments_by_doctor_and_date(doctor_id, date)
    return jsonify([clean(a) for a in (appts or [])])
