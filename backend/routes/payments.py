from flask import Blueprint, jsonify, request
from services.payment import (
    mark_payment_paid,
    mark_payment_refunded,
    get_payment_status,
    get_pending_payments,
)
from utils import clean_row as clean

payments_bp = Blueprint("payments", __name__)


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
    data = request.get_json(silent=True) or {}
    method = data.get("method", "cash")
    rows = mark_payment_paid(appointment_id, method)
    if not rows:
        return jsonify({"error": "No payment record found for that appointment"}), 404
    return jsonify({"message": "Payment recorded", "method": method})


@payments_bp.route("/<int:appointment_id>/refund", methods=["PATCH"])
def refund(appointment_id):
    rows = mark_payment_refunded(appointment_id)
    if not rows:
        return jsonify({"error": "No paid payment found to refund for that appointment"}), 404
    return jsonify({"message": "Refund processed"})
