from fastapi import FastAPI, Request
import sqlite3
from datetime import datetime, timedelta
import re

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

conn.commit()

# ---------------- CLINIC RULES ----------------
CLINIC_START = 9
CLINIC_END = 20
LUNCH_START = 13
LUNCH_END = 14

# ---------------- DATE PARSER (HINDI + ENG) ----------------
def normalize_date(text):
    if not text:
        return None

    t = text.lower().strip()
    today = datetime.now()

    # Hindi + English keywords
    if "aaj" in t or "today" in t:
        return today
    if "kal" in t or "tomorrow" in t:
        return today + timedelta(days=1)
    if "parso" in t:
        return today + timedelta(days=2)

    # "3 tarikh", "5 date"
    m = re.search(r'(\d{1,2})\s*(tarikh|date)?', t)
    if m:
        day = int(m.group(1))
        try:
            return today.replace(day=day)
        except:
            pass

    # Try standard formats
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(t, fmt)
        except:
            pass

    return None

# ---------------- TIME PARSER (HINDI + ENG) ----------------
def normalize_time(text):
    if not text:
        return None

    t = text.lower().strip().replace(".", "")

    # "2 baje", "2 pm", "2:30 pm"
    m = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|baje)?', t)
    if m:
        h = int(m.group(1))
        mnt = int(m.group(2)) if m.group(2) else 0
        p = m.group(3)

        if p in ["pm"] and h != 12:
            h += 12
        if p in ["am"] and h == 12:
            h = 0

        return h

    return None

# ---------------- VALIDATION ----------------
def validate_slot(date_obj, hour):
    if date_obj.weekday() == 6:
        return False, "Clinic is closed on Sundays."

    if hour < CLINIC_START or hour >= CLINIC_END:
        return False, "Clinic is open from 9 AM to 8 PM."

    if LUNCH_START <= hour < LUNCH_END:
        return False, "Doctor is unavailable during lunch (1 PM–2 PM)."

    return True, "valid"

# ---------------- CHECK AVAILABILITY ----------------
def is_available(doctor, date_obj, hour):
    cursor.execute(
        "SELECT * FROM bookings WHERE doctor=? AND date=? AND time=?",
        (doctor, date_obj.strftime("%Y-%m-%d"), f"{hour:02d}:00")
    )
    return cursor.fetchone() is None

# ---------------- NEXT SLOT ----------------
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

# ---------------- BOOK ----------------
@app.post("/book")
async def book(request: Request):
    data = await request.json()

    print("RAW:", data)

    # Handle Retell formats
    if "args" in data:
        data = data["args"]
    elif "arguments" in data:
        data = data["arguments"]

    name = data.get("name")
    doctor = data.get("doctor")
    raw_date = data.get("date")
    raw_time = data.get("time")

    date_obj = normalize_date(raw_date)
    hour = normalize_time(raw_time)

    print("PARSED:", name, doctor, date_obj, hour)

    if not all([name, doctor, date_obj, hour is not None]):
        return {"status": "error", "message": "Invalid input"}

    # Validate
    valid, msg = validate_slot(date_obj, hour)
    if not valid:
        return {"status": "error", "message": msg}

    # Check availability
    if not is_available(doctor, date_obj, hour):
        nxt = next_available(doctor, date_obj)
        if nxt:
            return {
                "status": "unavailable",
                "message": f"Slot not available. Next available slot is {nxt}:00."
            }
        else:
            return {"status": "unavailable", "message": "No slots available"}

    # Save booking
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

    return {
        "status": "confirmed",
        "date": date_obj.strftime("%Y-%m-%d"),
        "time": f"{hour:02d}:00"
    }
