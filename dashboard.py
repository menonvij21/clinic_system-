import streamlit as st
import requests
import pandas as pd
import time

# 🔥 CHANGE THIS to your Render URL
BASE_URL = "https://clinic-system-m69l.onrender.com"

st.set_page_config(page_title="Apollo Clinic Dashboard", layout="wide")

st.title("Apollo Clinic Dashboard")

# ---------------- FETCH FUNCTION ----------------
def fetch(endpoint):
    try:
        res = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        if res.status_code == 200:
            return res.json()
        else:
            return {"error": f"Error {res.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# ---------------- STATS ----------------
st.subheader("Stats")

stats = fetch("/api/stats")

if "error" in stats:
    st.error(stats["error"])
else:
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Calls", stats.get("total_calls", 0))
    col2.metric("Total Bookings", stats.get("total_bookings", 0))
    col3.metric("Bookings Today", stats.get("bookings_today", 0))

# ---------------- BOOKINGS ----------------
st.subheader("Bookings")

bookings_data = fetch("/api/bookings")

if "error" in bookings_data:
    st.error(bookings_data["error"])
else:
    bookings = bookings_data.get("bookings", [])

    if bookings:
        df = pd.DataFrame(bookings)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No bookings yet")

# ---------------- CALL LOGS ----------------
st.subheader("Call Logs")

calls_data = fetch("/api/call-logs")

if "error" in calls_data:
    st.error(calls_data["error"])
else:
    calls = calls_data.get("call_logs", [])

    if calls:
        df = pd.DataFrame(calls)

        # Show main table
        st.dataframe(df.drop(columns=["transcript"]), use_container_width=True)

        # Expand transcript view
        st.markdown("### Transcripts")
        for c in calls[:5]:
            with st.expander(f"Call {c['call_id']}"):
                st.text(c["transcript"])
    else:
        st.info("No calls yet")

# ---------------- AUTO REFRESH ----------------
st.caption("Auto-refresh every 10 seconds")
time.sleep(10)
st.rerun()
