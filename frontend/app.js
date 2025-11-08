/* ============================================================
   MediSchedule — Frontend App Logic
   Connects to Flask API at http://localhost:5000/api
   ============================================================ */

const API = "/api";

// ── STATE ──────────────────────────────────────────────────────

const state = {
  doctors: [],
  currentPayApptId: null,
  selectedPayMethod: "cash",
};


// ── UTILS ──────────────────────────────────────────────────────

function $(id) { return document.getElementById(id); }
function $$(sel) { return document.querySelectorAll(sel); }

function toast(msg, type = "") {
  const el = $("toast");
  el.textContent = msg;
  el.className = `toast show ${type}`;
  setTimeout(() => el.classList.remove("show"), 3500);
}

function formatDate(str) {
  if (!str) return "—";
  const d = new Date(str + "T00:00:00");
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

function formatTime(str) {
  if (!str) return "—";
  const [h, m] = str.split(":");
  const hr = parseInt(h);
  return `${hr > 12 ? hr - 12 : hr || 12}:${m} ${hr >= 12 ? "PM" : "AM"}`;
}

function getInitials(name) {
  return name.split(" ").slice(0, 2).map(w => w[0]).join("").toUpperCase();
}

async function api(path, opts = {}) {
  try {
    const res = await fetch(`${API}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...opts,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Request failed");
    return { ok: true, data };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}


// ── NAVIGATION ─────────────────────────────────────────────────

function navigate(viewId) {
  $$(".view").forEach(v => v.classList.remove("active"));
  $$(".nav-item").forEach(n => n.classList.remove("active"));

  const view = $(`view-${viewId}`);
  const navItem = document.querySelector(`[data-view="${viewId}"]`);
  if (view) view.classList.add("active");
  if (navItem) navItem.classList.add("active");

  // lazy-load view data
  if (viewId === "dashboard") loadDashboard();
  if (viewId === "doctors") renderDoctors();
  if (viewId === "payments") loadPendingPayments();
}

$$(".nav-item").forEach(item => {
  item.addEventListener("click", e => {
    e.preventDefault();
    navigate(item.dataset.view);
  });
});

// "View all" buttons
$$("[data-view]").forEach(btn => {
  if (!btn.classList.contains("nav-item")) {
    btn.addEventListener("click", () => navigate(btn.dataset.view));
  }
});


// ── API HEALTH CHECK ───────────────────────────────────────────

async function checkHealth() {
  const dot = document.querySelector(".dot");
  const statusText = document.querySelector(".status-text");
  const res = await api("/health");
  if (res.ok) {
    dot.classList.add("online");
    statusText.textContent = "API connected";
  } else {
    dot.classList.add("offline");
    statusText.textContent = "API offline";
    toast("Cannot reach the backend. Is Flask running on port 5000?", "error");
  }
}


// ── DASHBOARD ──────────────────────────────────────────────────

async function loadDashboard() {
  // date
  $("header-date").textContent = new Date().toLocaleDateString("en-IN", {
    weekday: "long", day: "numeric", month: "long", year: "numeric"
  });

  // fetch in parallel
  const [docRes, apptRes, payRes] = await Promise.all([
    api("/doctors/"),
    api("/appointments/"),
    api("/payments/pending"),
  ]);

  if (docRes.ok) {
    state.doctors = docRes.data;
    $("stat-doctors").textContent = docRes.data.length;
  }

  if (apptRes.ok) {
    const all = apptRes.data;
    $("stat-all").textContent = all.length;

    const today = new Date().toISOString().split("T")[0];
    const todayCount = all.filter(a => a.appointment_date === today).length;
    $("stat-today").textContent = todayCount;

    renderAppointmentsTable(all.slice(0, 8), "dashboard-appointments", false);
  }

  if (payRes.ok) {
    $("stat-pending").textContent = payRes.data.length;
  }
}


function renderAppointmentsTable(appts, containerId, showActions = true) {
  const container = $(containerId);
  if (!appts || appts.length === 0) {
    container.innerHTML = `<div class="empty-state"><p>No appointments found.</p></div>`;
    return;
  }

  const rows = appts.map(a => `
    <tr>
      <td><strong>#${a.appointment_id}</strong></td>
      <td>${a.patient_name || "—"}</td>
      <td>${a.doctor_name || "—"}</td>
      <td>${formatDate(a.appointment_date)}</td>
      <td>${formatTime(a.appointment_time)}</td>
      <td><span class="badge badge-${a.status}">${a.status}</span></td>
      <td><span class="badge badge-${a.payment_status || 'pending'}">${a.payment_status || 'pending'}</span></td>
      ${showActions ? `
      <td>
        ${a.status === "scheduled" ? `<button class="action-btn btn-cancel" onclick="cancelAppt(${a.appointment_id})">Cancel</button>` : ""}
      </td>` : "<td></td>"}
    </tr>
  `).join("");

  container.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Patient</th>
          <th>Doctor</th>
          <th>Date</th>
          <th>Time</th>
          <th>Status</th>
          <th>Payment</th>
          <th></th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}


// ── BOOK APPOINTMENT ───────────────────────────────────────────

async function loadDoctorsForBooking() {
  const res = await api("/doctors/");
  if (!res.ok) return;

  state.doctors = res.data;
  const select = $("b-doctor");
  select.innerHTML = '<option value="">— Select a doctor —</option>' +
    res.data.map(d => `<option value="${d.doctor_id}">${d.name} — ${d.specialization}</option>`).join("");
}

$("b-doctor").addEventListener("change", maybeLoadSlots);
$("b-date").addEventListener("change", maybeLoadSlots);

async function maybeLoadSlots() {
  const doctorId = $("b-doctor").value;
  const date = $("b-date").value;
  const slotSelect = $("b-slot");

  if (!doctorId || !date) {
    slotSelect.innerHTML = "<option>Pick a doctor & date first</option>";
    slotSelect.disabled = true;
    return;
  }

  slotSelect.innerHTML = "<option>Loading slots...</option>";
  slotSelect.disabled = true;

  const res = await api(`/doctors/${doctorId}/slots?date=${date}`);
  if (!res.ok || res.data.slots.length === 0) {
    slotSelect.innerHTML = "<option>No slots available</option>";
    return;
  }

  slotSelect.innerHTML = res.data.slots.map(s => `<option value="${s}">${formatTime(s + ":00")}</option>`).join("");
  slotSelect.disabled = false;
}

$("btn-book").addEventListener("click", async () => {
  const name    = $("b-name").value.trim();
  const email   = $("b-email").value.trim();
  const phone   = $("b-phone").value.trim();
  const dob     = $("b-dob").value;
  const doctor  = $("b-doctor").value;
  const date    = $("b-date").value;
  const time    = $("b-slot").value;
  const reason  = $("b-reason").value.trim();

  if (!name || !email || !doctor || !date || !time || time.includes("Pick") || time.includes("No ")) {
    toast("Please fill all required fields and select a time slot.", "error");
    return;
  }

  const btn = $("btn-book");
  btn.textContent = "Booking...";
  btn.disabled = true;

  const res = await api("/appointments/", {
    method: "POST",
    body: JSON.stringify({ name, email, phone, date_of_birth: dob, doctor_id: parseInt(doctor), date, time, reason }),
  });

  btn.textContent = "Confirm Booking";
  btn.disabled = false;

  if (!res.ok) {
    toast(res.error, "error");
    return;
  }

  const d = res.data;
  $("book-success-msg").textContent =
    `Appointment #${d.appointment_id} booked. Consultation fee ₹${d.fee} is due at the clinic.`;
  $("book-success").classList.remove("hidden");
  toast("Appointment booked successfully!", "success");

  // reset form
  ["b-name","b-email","b-phone","b-reason"].forEach(id => $(id).value = "");
  $("b-dob").value = "";
  $("b-date").value = "";
  $("b-doctor").value = "";
  $("b-slot").innerHTML = "<option>Pick a date first</option>";
  $("b-slot").disabled = true;
});


// ── MY APPOINTMENTS ────────────────────────────────────────────

$("btn-search-appts").addEventListener("click", searchPatientAppts);
$("appt-email").addEventListener("keydown", e => { if (e.key === "Enter") searchPatientAppts(); });

async function searchPatientAppts() {
  const email = $("appt-email").value.trim();
  if (!email) { toast("Enter a patient email first.", "error"); return; }

  $("appt-results").innerHTML = `<div class="loading-state">Searching...</div>`;

  const patRes = await api(`/patients/lookup?email=${encodeURIComponent(email)}`);
  if (!patRes.ok) {
    $("appt-results").innerHTML = `<div class="empty-state"><p>No patient found with that email.</p></div>`;
    return;
  }

  const patient = patRes.data;
  const apptRes = await api(`/patients/${patient.patient_id}/appointments`);
  const appts = apptRes.ok ? apptRes.data : [];

  $("appt-results").innerHTML = `
    <div class="patient-info-bar">
      <span><strong>${patient.name}</strong></span>
      <span>${patient.email}</span>
      ${patient.phone ? `<span>📞 ${patient.phone}</span>` : ""}
      <span style="margin-left:auto; color: var(--text-muted)">Patient ID: ${patient.patient_id}</span>
    </div>
    <div class="table-wrap" id="patient-appts-table"></div>
  `;

  renderAppointmentsTable(appts, "patient-appts-table", true);
}

window.cancelAppt = async function(apptId) {
  if (!confirm(`Cancel appointment #${apptId}?`)) return;
  const res = await api(`/appointments/${apptId}/cancel`, { method: "PATCH" });
  if (res.ok) {
    toast("Appointment cancelled.", "success");
    searchPatientAppts();
    loadDashboard();
  } else {
    toast(res.error, "error");
  }
};


// ── DOCTORS ────────────────────────────────────────────────────

async function renderDoctors(filter = "") {
  const grid = $("doctors-grid");

  if (!state.doctors.length) {
    grid.innerHTML = `<div class="loading-state">Loading doctors...</div>`;
    const res = await api("/doctors/");
    if (!res.ok) { grid.innerHTML = `<div class="empty-state"><p>Failed to load doctors.</p></div>`; return; }
    state.doctors = res.data;
  }

  const filtered = filter
    ? state.doctors.filter(d =>
        d.specialization.toLowerCase().includes(filter.toLowerCase()) ||
        d.name.toLowerCase().includes(filter.toLowerCase()))
    : state.doctors;

  if (!filtered.length) {
    grid.innerHTML = `<div class="empty-state"><p>No doctors match your search.</p></div>`;
    return;
  }

  grid.innerHTML = filtered.map(d => `
    <div class="doctor-card">
      <div class="doctor-avatar">${getInitials(d.name)}</div>
      <div class="doctor-name">${d.name}</div>
      <div class="doctor-spec">${d.specialization}</div>
      <div class="doctor-meta">
        <span>📞 ${d.phone || "N/A"}</span>
        <span>🕐 ${formatTime(d.available_from + ":00")} – ${formatTime(d.available_to + ":00")}</span>
      </div>
      <button class="doc-book-btn" onclick="bookWithDoctor(${d.doctor_id})">Book Appointment →</button>
    </div>
  `).join("");
}

$("doc-filter").addEventListener("input", e => renderDoctors(e.target.value));

window.bookWithDoctor = function(doctorId) {
  navigate("book");
  setTimeout(() => {
    $("b-doctor").value = doctorId;
    $("b-doctor").dispatchEvent(new Event("change"));
  }, 100);
};


// ── PAYMENTS ───────────────────────────────────────────────────

async function loadPendingPayments() {
  const container = $("payments-table");
  container.innerHTML = `<div class="loading-state">Loading...</div>`;

  const res = await api("/payments/pending");
  if (!res.ok) {
    container.innerHTML = `<div class="empty-state"><p>Failed to load payments.</p></div>`;
    return;
  }

  const payments = res.data;
  if (!payments.length) {
    container.innerHTML = `<div class="empty-state"><p>No pending payments. All caught up! ✓</p></div>`;
    return;
  }

  const rows = payments.map(p => `
    <tr>
      <td><strong>#${p.appointment_id}</strong></td>
      <td>${p.patient_name}</td>
      <td>${p.doctor_name}</td>
      <td>${formatDate(p.appointment_date)}</td>
      <td><strong>₹${parseFloat(p.amount).toLocaleString("en-IN")}</strong></td>
      <td><span class="badge badge-pending">Pending</span></td>
      <td><button class="action-btn btn-pay" onclick="openPayModal(${p.appointment_id})">Record Payment</button></td>
    </tr>
  `).join("");

  container.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Appt ID</th>
          <th>Patient</th>
          <th>Doctor</th>
          <th>Date</th>
          <th>Amount</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

window.openPayModal = function(apptId) {
  state.currentPayApptId = apptId;
  state.selectedPayMethod = "cash";
  $("pay-appt-id").textContent = apptId;
  $$(".method-btn").forEach(b => b.classList.toggle("active", b.dataset.method === "cash"));
  $("pay-modal").classList.remove("hidden");
};

$$(".method-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    state.selectedPayMethod = btn.dataset.method;
    $$(".method-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
  });
});

$("pay-cancel").addEventListener("click", () => $("pay-modal").classList.add("hidden"));

$("pay-confirm").addEventListener("click", async () => {
  const res = await api(`/payments/${state.currentPayApptId}/pay`, {
    method: "PATCH",
    body: JSON.stringify({ method: state.selectedPayMethod }),
  });

  $("pay-modal").classList.add("hidden");

  if (res.ok) {
    toast("Payment recorded successfully!", "success");
    loadPendingPayments();
    loadDashboard();
  } else {
    toast(res.error || "Failed to record payment.", "error");
  }
});

// close modal on overlay click
$("pay-modal").addEventListener("click", e => {
  if (e.target === $("pay-modal")) $("pay-modal").classList.add("hidden");
});


// ── INIT ───────────────────────────────────────────────────────

(async function init() {
  await checkHealth();
  await loadDoctorsForBooking();

  // set min date to today for booking
  const today = new Date().toISOString().split("T")[0];
  $("b-date").min = today;

  loadDashboard();
})();
