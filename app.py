from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime, date

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("clinic.db", check_same_thread=False)
cursor = conn.cursor()

# ---------------- TABLES ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    doctor TEXT,
    date TEXT,
    time TEXT,
    status TEXT,
    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS calls (
    id TEXT,
    user_input TEXT,
    agent_response TEXT,
    transcript TEXT,
    duration_seconds INTEGER,
    outcome TEXT,
    timestamp TEXT
)
""")

conn.commit()

# ---------------- SAFE MIGRATION ----------------
def safe_add_column(table, column, col_type):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
    except:
        pass

safe_add_column("bookings", "status", "TEXT")
safe_add_column("bookings", "timestamp", "TEXT")
safe_add_column("calls", "transcript", "TEXT")
safe_add_column("calls", "duration_seconds", "INTEGER")
safe_add_column("calls", "outcome", "TEXT")

conn.commit()

# ---------------- MEMORY ----------------
sessions = {}

# ---------------- CHAT ----------------
@app.post("/chat")
async def chat(data: dict):
    message = data.get("message", "")
    call_id = data.get("call_id", "default")

    memory = sessions.setdefault(call_id, {"history": ""})

    response = "Got it."

    memory["history"] += f"\nUser: {message}\nAI: {response}"

    if len(memory["history"]) > 2000:
        memory["history"] = memory["history"][-2000:]

    transcript = memory["history"]

    cursor.execute("""
    INSERT INTO calls (id, user_input, agent_response, transcript, duration_seconds, outcome, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        call_id,
        message,
        response,
        transcript,
        60,
        "completed",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()

    return {"response": response}

# ---------------- BOOK ----------------
@app.post("/book")
async def book(data: dict):

    # 🔥 Handle Retell format
    if "args" in data:
        data = data["args"]

    name = data.get("name")
    doctor = data.get("doctor")
    booking_date = data.get("date")
    booking_time = data.get("time")

    if not all([name, doctor, booking_date, booking_time]):
        return {
            "status": "error",
            "message": "Missing required fields"
        }

    # ✅ Validate date
    try:
        dt = datetime.strptime(booking_date, "%Y-%m-%d")
    except:
        return {
            "status": "error",
            "message": "Invalid date format"
        }

    # ❌ No Sunday
    if dt.weekday() == 6:
        return {
            "status": "closed",
            "message": "Clinic is closed on Sunday"
        }

    # ❌ Prevent double booking
    cursor.execute("""
    SELECT id FROM bookings 
    WHERE doctor=? AND date=? AND time=?
    """, (doctor, booking_date, booking_time))

    if cursor.fetchone():
        return {
            "status": "unavailable",
            "message": "This slot is already booked"
        }

    # ✅ Insert booking
    cursor.execute("""
    INSERT INTO bookings (name, doctor, date, time, status, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        doctor,
        booking_date,
        booking_time,
        "confirmed",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()

    return {
        "status": "confirmed",
        "message": f"Appointment booked with {doctor} on {booking_date} at {booking_time}"
    }

# ---------------- API: STATS ----------------
@app.get("/api/stats")
def stats():
    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM calls")
    total_calls = cursor.fetchone()[0]

    today = date.today().strftime("%Y-%m-%d")

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE date=?", (today,))
    today_bookings = cursor.fetchone()[0]

    return {
        "total_bookings": total_bookings,
        "total_calls": total_calls,
        "bookings_today": today_bookings
    }

# ---------------- API: BOOKINGS ----------------
@app.get("/api/bookings")
def get_bookings():
    cursor.execute("""
    SELECT id, name, doctor, date, time, status
    FROM bookings
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    return {
        "bookings": [
            {
                "id": r[0],
                "patient_name": r[1],
                "doctor_name": r[2],
                "appointment_date": r[3],
                "appointment_time": r[4],
                "status": r[5] if r[5] else "confirmed"
            }
            for r in rows
        ]
    }

# ---------------- API: CALL LOGS ----------------
@app.get("/api/call-logs")
def get_calls():
    cursor.execute("""
    SELECT id, transcript, duration_seconds, outcome, timestamp
    FROM calls
    ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()

    return {
        "call_logs": [
            {
                "call_id": r[0],
                "call_started_at": r[4],
                "duration_seconds": r[2] if r[2] else 60,
                "outcome": r[3] if r[3] else "completed",
                "transcript": r[1] if r[1] else ""
            }
            for r in rows
        ]
    }

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "running"}
