import datetime
from flask import Blueprint, jsonify, request
from services.payment import (
    mark_payment_paid,
    mark_payment_refunded,
    get_payment_status,
    get_pending_payments,
)

payments_bp = Blueprint("payments", __name__)


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


@payments_bp.route("/pending", methods=["GET"])
def pending_payments():
    pending = get_pending_payments()
    return jsonify([clean(p) for p in (pending or [])])


@payments_bp.route("/<int:appointment_id>", methods=["GET"])
def payment_status(appointment_id):
    payment = get_payment_status(appointment_id)
    if not payment:
        return jsonify({"error": "No payment record found"}), 404
    return jsonify(clean(payment))


@payments_bp.route("/<int:appointment_id>/pay", methods=["PATCH"])
def pay(appointment_id):
    data = request.get_json() or {}
    method = data.get("method", "cash")
    mark_payment_paid(appointment_id, method)
    return jsonify({"message": "Payment recorded", "method": method})


@payments_bp.route("/<int:appointment_id>/refund", methods=["PATCH"])
def refund(appointment_id):
    mark_payment_refunded(appointment_id)
    return jsonify({"message": "Refund processed"})
