# MediSchedule — Hospital Appointment Scheduling System

A full-stack hospital appointment management system built with **Python (Flask)** on the backend and **vanilla HTML/CSS/JS** on the frontend.

![Tech Stack](https://img.shields.io/badge/Backend-Flask%20%2B%20MySQL-1a6b7c) ![Frontend](https://img.shields.io/badge/Frontend-HTML%20%2F%20CSS%20%2F%20JS-d95f3b)

---

## Features

- **Book appointments** — real-time slot availability check, auto-registers new patients
- **Patient lookup** — search appointments by email, view full history
- **Doctor directory** — browse specialists with availability hours, click to book
- **Payment tracking** — pending payment queue, record cash/card/UPI/insurance
- **Cancellation management** — cancel with one click, payment flag for refund
- **Automated reminders** — email alerts 24 hours before appointment (cron-ready)
- **Daily doctor summaries** — morning email with the day's schedule

---

## Project Structure

```
hospital-system/
├── backend/
│   ├── app.py               # Flask entry point + blueprint registration
│   ├── config.py            # Env-based configuration
│   ├── db.py                # MySQL connection helper
│   ├── schema.sql           # DB setup script (run once)
│   ├── .env.example         # Copy to .env and fill in
│   ├── requirements.txt
│   ├── models/
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   └── appointment.py
│   ├── routes/
│   │   ├── appointments.py  # POST/GET/PATCH /api/appointments
│   │   ├── doctors.py       # GET /api/doctors, GET /api/doctors/:id/slots
│   │   ├── patients.py      # POST/GET /api/patients
│   │   └── payments.py      # PATCH /api/payments/:id/pay
│   └── services/
│       ├── payment.py
│       └── reminder.py
└── frontend/
    ├── index.html           # Single-page app shell
    ├── styles.css           # Full custom design system
    └── app.js               # API calls, routing, UI logic
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/doctors/` | List all doctors |
| GET | `/api/doctors/:id/slots?date=YYYY-MM-DD` | Available time slots |
| POST | `/api/patients/` | Register patient |
| GET | `/api/patients/lookup?email=` | Find patient by email |
| GET | `/api/patients/:id/appointments` | Patient's appointment history |
| GET | `/api/appointments/` | All appointments |
| POST | `/api/appointments/` | Book new appointment |
| PATCH | `/api/appointments/:id/cancel` | Cancel appointment |
| GET | `/api/payments/pending` | Pending payment list |
| PATCH | `/api/payments/:id/pay` | Record payment |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/hospital-appointment-system.git
cd hospital-appointment-system
```

### 2. Set up the database

```bash
mysql -u root -p < backend/schema.sql
```

### 3. Configure the backend

```bash
cd backend
cp .env.example .env
# Edit .env with your MySQL credentials and email settings
```

### 4. Install dependencies and run Flask

```bash
pip install -r requirements.txt
python app.py
# Flask starts at http://localhost:5000
```

### 5. Open the frontend

Just open `frontend/index.html` in your browser. It talks to the Flask API at `localhost:5000`.

> For a better dev experience, use a simple server like `python -m http.server 8080` inside the `frontend/` folder.

---

## Automated Tasks

Run these as cron jobs to send reminders and daily summaries:

```bash
# Reminder emails — run daily at 8 AM
0 8 * * * cd /path/to/backend && python -c "from services.reminder import send_reminders; send_reminders()"
```

---

## Tech Stack

- **Backend** — Python 3, Flask, Flask-CORS, mysql-connector-python
- **Database** — MySQL
- **Frontend** — HTML5, CSS3, Vanilla JavaScript (no frameworks)
- **Email** — Python smtplib + Gmail SMTP

## License

MIT

## 🌐 Live Demo
[https://hospital-appointment-scheduling-sys.vercel.app](https://hospital-appointment-scheduling-sys.vercel.app)
