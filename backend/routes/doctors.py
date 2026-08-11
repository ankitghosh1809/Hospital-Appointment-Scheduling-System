import datetime
from flask import Blueprint, jsonify, request
from models.doctor import get_all_doctors, get_doctor_by_id, get_doctors_by_specialization, add_doctor
from models.appointment import get_appointments_by_doctor_and_date, is_slot_available
from utils import clean_row, to_jsonable
from config import HOSPITAL_TZ

doctors_bp = Blueprint("doctors", __name__)


@doctors_bp.route("/", methods=["GET"])
def list_doctors():
    spec = request.args.get("specialization")
    if spec:
        doctors = get_doctors_by_specialization(spec)
    else:
        doctors = get_all_doctors()

    return jsonify([clean_row(d) for d in (doctors or [])])


@doctors_bp.route("/<int:doctor_id>", methods=["GET"])
def get_doctor(doctor_id):
    doctor = get_doctor_by_id(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    return jsonify(clean_row(doctor))


@doctors_bp.route("/<int:doctor_id>/slots", methods=["GET"])
def get_slots(doctor_id):
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "date param required (YYYY-MM-DD)"}), 400

    doctor = get_doctor_by_id(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    booked = get_appointments_by_doctor_and_date(doctor_id, date)
    booked_times = set()
    for a in (booked or []):
        t = a["appointment_time"]
        if hasattr(t, "seconds"):
            total = int(t.total_seconds())
            booked_times.add(f"{total // 3600:02d}:{(total % 3600) // 60:02d}:00")
        else:
            booked_times.add(str(t))

    # parse available_from / available_to
    def td_to_str(td):
        if hasattr(td, "total_seconds"):
            total = int(td.total_seconds())
            return f"{total // 3600:02d}:{(total % 3600) // 60:02d}"
        return str(td)[:5]

    avail_from = td_to_str(doctor["available_from"])
    avail_to = td_to_str(doctor["available_to"])

    start = datetime.datetime.strptime(avail_from, "%H:%M")
    end = datetime.datetime.strptime(avail_to, "%H:%M")

    is_today = date == datetime.datetime.now(HOSPITAL_TZ).date().isoformat()
    now_time = datetime.datetime.now(HOSPITAL_TZ).time()

    slots = []
    current = start
    while current < end:
        slot_str = current.strftime("%H:%M:%S")
        slot_display = current.strftime("%H:%M")
        already_passed = is_today and current.time() <= now_time
        if slot_str not in booked_times and not already_passed:
            slots.append(slot_display)
        current += datetime.timedelta(minutes=30)

    return jsonify({"slots": slots, "date": date, "doctor": doctor["name"]})


@doctors_bp.route("/", methods=["POST"])
def create_doctor():
    data = request.get_json(silent=True) or {}
    required = ["name", "specialization", "email", "phone"]
    if not all(k in data for k in required):
        return jsonify({"error": "name, specialization, email, phone required"}), 400

    doc_id = add_doctor(
        data["name"],
        data["specialization"],
        data["email"],
        data["phone"],
        data.get("available_from", "09:00:00"),
        data.get("available_to", "17:00:00"),
    )
    return jsonify({"doctor_id": doc_id, "message": "Doctor added"}), 201
