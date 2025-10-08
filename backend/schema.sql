CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(15),
    available_from TIME DEFAULT '09:00:00',
    available_to TIME DEFAULT '17:00:00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(15),
    date_of_birth DATE,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    reason TEXT,
    status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method ENUM('cash', 'card', 'upi', 'insurance') DEFAULT 'cash',
    status ENUM('pending', 'paid', 'refunded') DEFAULT 'pending',
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

CREATE TABLE IF NOT EXISTS reminders (
    reminder_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reminder_type ENUM('email', 'sms') DEFAULT 'email',
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

INSERT IGNORE INTO doctors (name, specialization, email, phone, available_from, available_to) VALUES
('Dr. Priya Sharma', 'Cardiologist', 'priya.sharma@hospital.com', '9876543210', '09:00:00', '17:00:00'),
('Dr. Rahul Mehta', 'General Physician', 'rahul.mehta@hospital.com', '9876543211', '10:00:00', '18:00:00'),
('Dr. Anita Desai', 'Dermatologist', 'anita.desai@hospital.com', '9876543212', '09:00:00', '15:00:00'),
('Dr. Suresh Iyer', 'Orthopedic Surgeon', 'suresh.iyer@hospital.com', '9876543213', '08:00:00', '16:00:00'),
('Dr. Meera Nair', 'Pediatrician', 'meera.nair@hospital.com', '9876543214', '09:00:00', '17:00:00');
