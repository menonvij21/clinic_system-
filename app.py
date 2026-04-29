from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from datetime import datetime, timedelta
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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

# ---------------- CLINIC RULES ----------------
CLINIC_START = 9
CLINIC_END = 20
LUNCH_START = 13
LUNCH_END = 14

# ---------------- HELPERS ----------------
def normalize_date(text):
    if not text:
        return None
    t = text.lower().strip()
    today = datetime.now()

    if "aaj" in t or "today" in t:
        return today
    if "kal" in t or "tomorrow" in t:
        return today + timedelta(days=1)
    if "parso" in t:
        return today + timedelta(days=2)

    # "3 tarikh"
    m = re.search(r'(\d{1,2})', t)
    if m:
        day = int(m.group(1))
        try:
            return today.replace(day=day)
        except:
            pass

    try:
        return datetime.strptime(t, "%Y-%m-%d")
    except:
        return None

def normalize_time(text):
    if not text:
        return None
    t = text.lower().replace(".", "").strip()

    m = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|baje)?', t)
    if not m:
        return None

    h = int(m.group(1))
    p = m.group(3)

    if p == "pm" and h != 12:
        h += 12
    if p == "am" and h == 12:
        h = 0

    return h

def validate_slot(date_obj, hour):
    if date_obj.weekday() == 6:
        return False, "Clinic closed on Sunday"
    if hour < CLINIC_START or hour >= CLINIC_END:
        return False, "Clinic hours are 9 AM to 8 PM"
    if LUNCH_START <= hour < LUNCH_END:
        return False, "Lunch break 1–2 PM"
    return True, "ok"

def is_available(doctor, date_obj, hour):
    cursor.execute(
        "SELECT * FROM bookings WHERE doctor=? AND date=? AND time=?",
        (doctor, date_obj.strftime("%Y-%m-%d"), f"{hour:02d}:00")
    )
    return cursor.fetchone() is None

def next_available(doctor, date_obj):
    for h in range(CLINIC_START, CLINIC_END):
        if LUNCH_START <= h < LUNCH_END:
            continue
        if is_available(doctor, date_obj, h):
            return h
    return None

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "running"}

# ---------------- DASHBOARD PAGE ----------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ---------------- CHAT LOGGING ----------------
sessions = {}

@app.post("/chat")
async def chat(data: dict):
    message = data.get("message", "")
    call_id = data.get("call_id", "default")

    memory = sessions.setdefault(call_id, {"history": ""})
    response = "Got it."

    transcript = memory["history"] + f"\nUser: {message}\nAI: {response}"
    memory["history"] = transcript

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
async def book(request: Request):
    data = await request.json()

    if "args" in data:
        data = data["args"]
    elif "arguments" in data:
        data = data["arguments"]

    name = data.get("name")
    doctor = data.get("doctor")
    date_obj = normalize_date(data.get("date"))
    hour = normalize_time(data.get("time"))

    if not all([name, doctor, date_obj, hour is not None]):
        return {"status": "error", "message": "Invalid input"}

    valid, msg = validate_slot(date_obj, hour)
    if not valid:
        return {"status": "error", "message": msg}

    if not is_available(doctor, date_obj, hour):
        nxt = next_available(doctor, date_obj)
        return {
            "status": "unavailable",
            "message": f"Next available slot {nxt}:00" if nxt else "No slots available"
        }

    cursor.execute(
        "INSERT INTO bookings (name, doctor, date, time, status, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (
            name,
            doctor,
            date_obj.strftime("%Y-%m-%d"),
            f"{hour:02d}:00",
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
    b = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM calls")
    c = cursor.fetchone()[0]

    return {
        "total_bookings": b,
        "total_calls": c,
        "bookings_today": b,
        "avg_call_duration_seconds": 60
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
                "status": r[5]
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
