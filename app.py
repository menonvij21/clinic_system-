from fastapi import FastAPI, Request
import sqlite3
from datetime import datetime

app = FastAPI()

# ---------------- DATABASE ----------------
conn = sqlite3.connect("clinic.db", check_same_thread=False)
cursor = conn.cursor()

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

# ---------------- CHAT ----------------
sessions = {}

@app.post("/chat")
async def chat(data: dict):
    message = data.get("message", "")
    call_id = data.get("call_id", "default")

    memory = sessions.setdefault(call_id, {"history": ""})

    response = "Got it."

    # CLEAN TRANSCRIPT
    memory["history"] += f"\nUser: {message}\nAI: {response}"

    # LIMIT SIZE
    if len(memory["history"]) > 1000:
        memory["history"] = memory["history"][-1000:]

    transcript = memory["history"]

    cursor.execute(
        "INSERT INTO calls VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            call_id,
            message,
            response,
            transcript,
            60,
            "completed",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    conn.commit()

    return {"response": response}

# ---------------- BOOK ----------------
@app.post("/book")
async def book(data: dict):
    if "args" in data:
        data = data["args"]

    name = data.get("name")
    doctor = data.get("doctor")
    date = data.get("date")
    time = data.get("time")

    cursor.execute(
        "INSERT INTO bookings VALUES (NULL, ?, ?, ?, ?, ?, ?)",
        (
            name,
            doctor,
            date,
            time,
            "confirmed",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    conn.commit()

    return {"status": "confirmed"}

# ---------------- API: STATS ----------------
@app.get("/api/stats")
def stats():
    cursor.execute("SELECT COUNT(*) FROM bookings")
    bookings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM calls")
    calls = cursor.fetchone()[0]

    return {
        "total_bookings": bookings,
        "total_calls": calls,
        "bookings_today": bookings
    }

# ---------------- API: BOOKINGS ----------------
@app.get("/api/bookings")
def get_bookings():
    cursor.execute("SELECT id, name, doctor, date, time, status FROM bookings ORDER BY id DESC")
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
    cursor.execute("SELECT id, transcript, timestamp FROM calls ORDER BY timestamp DESC")
    rows = cursor.fetchall()

    return {
        "call_logs": [
            {
                "call_id": r[0],
                "call_started_at": r[2],
                "duration_seconds": 60,
                "outcome": "completed",
                "transcript": r[1]
            }
            for r in rows
        ]
    }

@app.get("/")
def root():
    return {"status": "running"}
