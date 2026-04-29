from fastapi import FastAPI
import sqlite3
from datetime import datetime
import threading

app = FastAPI()

# ---------------- DATABASE ----------------
# Fixed: Added check_same_thread=False AND a lock for thread safety
conn = sqlite3.connect("clinic.db", check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()  # Fix 1: Prevent race conditions on concurrent requests

# Create tables (latest schema)
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    doctor TEXT,
    date TEXT,
    time TEXT,
    status TEXT,
    created_at TEXT
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
    created_at TEXT
)
""")

# ---------------- AUTO MIGRATION ----------------
def safe_add_column(table, column, col_type):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        conn.commit()  # Fix 2: Commit each migration immediately
    except Exception:
        pass  # Fix 3: Silently ignore (column already exists)

safe_add_column("bookings", "status", "TEXT")
safe_add_column("bookings", "created_at", "TEXT")

safe_add_column("calls", "transcript", "TEXT")
safe_add_column("calls", "duration_seconds", "INTEGER")
safe_add_column("calls", "outcome", "TEXT")
safe_add_column("calls", "created_at", "TEXT")

conn.commit()

# ---------------- MEMORY ----------------
sessions = {}
sessions_lock = threading.Lock()  # Fix 4: Thread-safe session access

# ---------------- CHAT ----------------
@app.post("/chat")
async def chat(data: dict):
    message = data.get("message", "")
    call_id = data.get("call_id", "default")

    # Fix 5: Thread-safe session management
    with sessions_lock:
        memory = sessions.setdefault(call_id, {"history": ""})

        response = "Got it."

        memory["history"] += f"\nUser: {message}\nAI: {response}"

        # Fix 6: Trim from the START (not the end) to keep recent messages
        if len(memory["history"]) > 1000:
            memory["history"] = memory["history"][-1000:]

        transcript = memory["history"]

    # Fix 7: Thread-safe DB write
    with db_lock:
        cursor.execute("""
            INSERT INTO calls (id, user_input, agent_response, transcript, duration_seconds, outcome, created_at)
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
    if "args" in data:
        data = data["args"]

    name = data.get("name")
    doctor = data.get("doctor")
    date = data.get("date")
    time = data.get("time")

    # Fix 8: Validate required fields before DB insert
    if not all([name, doctor, date, time]):
        return {
            "status": "error",
            "message": "Missing required fields: name, doctor, date, time"
        }

    # Fix 9: Thread-safe DB write
    with db_lock:
        cursor.execute("""
            INSERT INTO bookings (name, doctor, date, time, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            doctor,
            date,
            time,
            "confirmed",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()

    return {"status": "confirmed"}

# ---------------- API: STATS ----------------
@app.get("/api/stats")
def stats():
    with db_lock:  # Fix 10: Thread-safe reads
        cursor.execute("SELECT COUNT(*) FROM bookings")
        total_bookings = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM calls")
        total_calls = cursor.fetchone()[0]

        # Fix 11: bookings_today now actually filters by today's date
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT COUNT(*) FROM bookings WHERE created_at LIKE ?",
            (f"{today}%",)
        )
        bookings_today = cursor.fetchone()[0]

    return {
        "total_bookings": total_bookings,
        "total_calls": total_calls,
        "bookings_today": bookings_today  # Fix 11 cont: was always == total_bookings
    }

# ---------------- API: BOOKINGS ----------------
@app.get("/api/bookings")
def get_bookings():
    with db_lock:  # Fix 12: Thread-safe read
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
    with db_lock:  # Fix 13: Thread-safe read
        cursor.execute("""
            SELECT id, created_at, duration_seconds, outcome, transcript 
            FROM calls 
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()

    return {
        "call_logs": [
            {
                "call_id": r[0],
                "call_started_at": r[1],
                "duration_seconds": r[2] if r[2] else 0,
                "outcome": r[3] if r[3] else "completed",
                "transcript": r[4] if r[4] else ""
            }
            for r in rows
        ]
    }

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "running"}
