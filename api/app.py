import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from routes.doctors import doctors_bp
from routes.patients import patients_bp
from routes.appointments import appointments_bp
from routes.payments import payments_bp

app = Flask(__name__)
CORS(app)  # allow frontend on any port during dev

app.register_blueprint(doctors_bp, url_prefix="/api/doctors")
app.register_blueprint(patients_bp, url_prefix="/api/patients")
app.register_blueprint(appointments_bp, url_prefix="/api/appointments")
app.register_blueprint(payments_bp, url_prefix="/api/payments")


@app.route("/api/health")
def health():
    return {"status": "ok", "message": "Hospital API is running"}


if __name__ == "__main__":
    app.run(debug=True, port=5000)
