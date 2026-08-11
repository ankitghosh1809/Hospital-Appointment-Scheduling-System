-- ============================================================
-- Hospital Management System - Database Schema
-- Engine : PostgreSQL (Neon)
-- ============================================================

CREATE TABLE IF NOT EXISTS doctors (
    doctor_id       SERIAL       PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    specialization  VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    phone           VARCHAR(15),
    available_from  TIME         DEFAULT '09:00:00',
    available_to    TIME         DEFAULT '17:00:00',
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS patients (
    patient_id    SERIAL       PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    phone         VARCHAR(15),
    date_of_birth DATE,
    address       TEXT,
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id   SERIAL PRIMARY KEY,
    patient_id       INT  NOT NULL REFERENCES patients(patient_id),
    doctor_id        INT  NOT NULL REFERENCES doctors(doctor_id),
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    reason           TEXT,
    status           VARCHAR(20) NOT NULL DEFAULT 'scheduled'
                      CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prevents two concurrent requests from both booking the same doctor's
-- slot (app-level check in is_slot_available() alone can't close this -
-- see models/appointment.py::book_appointment).
CREATE UNIQUE INDEX IF NOT EXISTS uniq_doctor_slot
    ON appointments (doctor_id, appointment_date, appointment_time)
    WHERE status = 'scheduled';

CREATE TABLE IF NOT EXISTS payments (
    payment_id      SERIAL         PRIMARY KEY,
    appointment_id  INT            NOT NULL REFERENCES appointments(appointment_id),
    amount          DECIMAL(10,2)  NOT NULL,
    payment_date    TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    payment_method  VARCHAR(20)    NOT NULL DEFAULT 'cash'
                     CHECK (payment_method IN ('cash', 'card', 'upi', 'insurance')),
    status          VARCHAR(20)    NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending', 'paid', 'refunded'))
);

CREATE TABLE IF NOT EXISTS reminders (
    reminder_id     SERIAL      PRIMARY KEY,
    appointment_id  INT         NOT NULL REFERENCES appointments(appointment_id),
    sent_at         TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    reminder_type   VARCHAR(10) NOT NULL DEFAULT 'email'
                     CHECK (reminder_type IN ('email', 'sms'))
);

INSERT INTO doctors (name, specialization, email, phone, available_from, available_to) VALUES
('Dr. Priya Sharma', 'Cardiologist',       'priya.sharma@hospital.com', '9876543210', '09:00:00', '17:00:00'),
('Dr. Rahul Mehta',  'General Physician',  'rahul.mehta@hospital.com',  '9876543211', '10:00:00', '18:00:00'),
('Dr. Anita Desai',  'Dermatologist',      'anita.desai@hospital.com',  '9876543212', '09:00:00', '15:00:00'),
('Dr. Suresh Iyer',  'Orthopedic Surgeon', 'suresh.iyer@hospital.com',  '9876543213', '08:00:00', '16:00:00'),
('Dr. Meera Nair',   'Pediatrician',       'meera.nair@hospital.com',   '9876543214', '09:00:00', '17:00:00')
ON CONFLICT (email) DO NOTHING;
