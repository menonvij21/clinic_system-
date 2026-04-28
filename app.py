from fastapi import FastAPI
from database import conn, cursor

# 🔥 THIS LINE WAS MISSING
app = FastAPI()

sessions = {}

def think(message: str, memory: dict):
    return "Got it."

@app.post("/chat")
async def chat(data: dict):
    message = data.get("message", "")
    call_id = data.get("call_id", "default")

    if call_id not in sessions:
        sessions[call_id] = {}

    memory = sessions[call_id]
    response = think(message, memory)

    # Save call log
    cursor.execute(
        "INSERT INTO calls (id, user_input, agent_response) VALUES (?, ?, ?)",
        (call_id, message, response)
    )
    conn.commit()

    return {"response": response}


@app.post("/book")
async def book(data: dict):
    name = data.get("name")
    doctor = data.get("doctor")
    date = data.get("date")
    time = data.get("time")

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

    cursor.execute(
        "INSERT INTO bookings (name, doctor, date, time) VALUES (?, ?, ?, ?)",
        (name, doctor, date, time)
    )
    conn.commit()

    return {"status": "confirmed"}