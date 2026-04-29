from fastapi import FastAPI, Request
import sqlite3
from datetime import datetime, timedelta

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
    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS calls (
    id TEXT,
    user_input TEXT,
    agent_response TEXT,
    timestamp TEXT
)
""")

conn.commit()

# ---------------- HELPERS ----------------
def normalize_date(date_str: str):
    if not date_str:
        return None

    s = date_str.lower().strip()

    if "aaj" in s or "today" in s:
        return datetime.now().strftime("%Y-%m-%d")

    if "kal" in s or "tomorrow" in s:
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # try parsing common formats
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except:
            pass

    return s  # fallback


def normalize_time(time_str: str):
    if not time_str:
        return None

    s = time_str.strip().lower().replace(".", "")

    try:
        return datetime.strptime(s, "%I %p").strftime("%H:%M")
    except:
        pass

    try:
        return datetime.strptime(s, "%I:%M %p").strftime("%H:%M")
    except:
        pass

    return time_str  # fallback


# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "running"}


# ---------------- CHAT (LOGGING) ----------------
sessions = {}

def think(message: str, memory: dict):
    return "Got it."

@app.post("/chat")
async def chat(data: dict):
    message = data.get("message", "")
    call_id = data.get("call_id", "default")

    if call_id not in sessions:
        sessions[call_id] = {}

    response = think(message, sessions[call_id])

    cursor.execute(
        "INSERT INTO calls (id, user_input, agent_response, timestamp) VALUES (?, ?, ?, ?)",
        (call_id, message, response, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()

    return {"response": response}


# ---------------- BOOK APPOINTMENT ----------------
@app.post("/book")
async def book(request: Request):
    data = await request.json()

    print("🔥 RAW DATA:", data)

    # Handle Retell formats
    if isinstance(data, dict):
        if "args" in data:
            data = data["args"]
        elif "arguments" in data:
            data = data["arguments"]

    name = data.get("name")
    doctor = data.get("doctor")
    date = normalize_date(data.get("date"))
    time = normalize_time(data.get("time"))

    print("✅ PARSED:", name, doctor, date, time)

    if not all([name, doctor, date, time]):
        return {
            "status": "error",
            "message": "Missing or invalid fields",
            "received": data
        }

    # Check duplicate booking
    cursor.execute(
        "SELECT * FROM bookings WHERE doctor=? AND date=? AND time=?",
        (doctor, date, time)
    )

    if cursor.fetchone():
        return {
            "status": "unavailable",
            "message": "Slot already booked"
        }

    # Save booking
    cursor.execute(
        "INSERT INTO bookings (name, doctor, date, time, timestamp) VALUES (?, ?, ?, ?, ?)",
        (name, doctor, date, time, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()

    return {"status": "confirmed"}


# ---------------- GET BOOKINGS ----------------
@app.get("/bookings")
def get_bookings():
    cursor.execute(
        "SELECT name, doctor, date, time, timestamp FROM bookings ORDER BY id DESC"
    )
    rows = cursor.fetchall()

    return {
        "bookings": [
            {
                "name": r[0],
                "doctor": r[1],
                "date": r[2],
                "time": r[3],
                "timestamp": r[4]
            }
            for r in rows
        ]
    }


# ---------------- GET CALL LOGS ----------------
@app.get("/calls")
def get_calls():
    cursor.execute(
        "SELECT id, user_input, agent_response, timestamp FROM calls ORDER BY timestamp DESC"
    )
    rows = cursor.fetchall()

    return {
        "calls": [
            {
                "id": r[0],
                "user_input": r[1],
                "agent_response": r[2],
                "timestamp": r[3]
            }
            for r in rows
        ]
    }
        ]
    }
