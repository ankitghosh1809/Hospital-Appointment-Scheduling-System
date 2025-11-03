from flask import Blueprint, jsonify, request
from models.patient import add_patient, get_patient_by_email, get_patient_by_id, get_all_patients
from models.appointment import get_appointments_by_patient

patients_bp = Blueprint("patients", __name__)


def serialize(obj):
    """Convert date/timedelta objects to strings for JSON."""
    import datetime
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return str(obj)
    return obj


def clean(row):
    return {k: serialize(v) for k, v in row.items()}


@patients_bp.route("/", methods=["GET"])
def list_patients():
    patients = get_all_patients()
    return jsonify([clean(p) for p in (patients or [])])


@patients_bp.route("/", methods=["POST"])
def create_patient():
    data = request.get_json()
    if not data.get("name") or not data.get("email"):
        return jsonify({"error": "name and email are required"}), 400

    existing = get_patient_by_email(data["email"])
    if existing:
        return jsonify({"patient_id": existing["patient_id"], "existing": True}), 200

    patient_id = add_patient(
        data["name"],
        data["email"],
        data.get("phone"),
        data.get("date_of_birth"),
        data.get("address"),
    )
    if not patient_id:
        return jsonify({"error": "Failed to register patient"}), 500

    return jsonify({"patient_id": patient_id, "message": "Patient registered"}), 201


@patients_bp.route("/lookup", methods=["GET"])
def lookup_by_email():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "email param required"}), 400

    patient = get_patient_by_email(email)
    if not patient:
        return jsonify({"error": "Not found"}), 404

    return jsonify(clean(patient))


@patients_bp.route("/<int:patient_id>/appointments", methods=["GET"])
def patient_appointments(patient_id):
    appointments = get_appointments_by_patient(patient_id)
    result = []
    for a in (appointments or []):
        result.append(clean(a))
    return jsonify(result)
