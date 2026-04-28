import streamlit as st
import requests
import pandas as pd

BASE_URL = "https://clinic-system-m69l.onrender.com"

st.set_page_config(page_title="Apollo Clinic Dashboard", layout="wide")

st.title("Apollo Clinic Dashboard")

# ------------------ BOOKINGS ------------------
st.header("Bookings")

try:
    res = requests.get(f"{BASE_URL}/bookings", timeout=10)

    if res.status_code == 200:
        data = res.json().get("bookings", [])

        if data:
            df = pd.DataFrame(data)

            # Optional: rename columns nicely if needed
            df.columns = ["Name", "Doctor", "Date", "Time", "Timestamp"][:len(df.columns)]

            st.dataframe(df, use_container_width=True)
        else:
            st.info("No bookings yet")
    else:
        st.error(f"Failed to fetch bookings (status {res.status_code})")

except Exception as e:
    st.error(f"Error fetching bookings: {e}")


# ------------------ CALL LOGS ------------------
st.header("Call Logs")

try:
    res = requests.get(f"{BASE_URL}/calls", timeout=10)

    if res.status_code == 200:
        data = res.json().get("calls", [])

        if data:
            df = pd.DataFrame(data)

            # Optional rename
            df.columns = ["Call ID", "User Input", "Agent Response", "Timestamp"][:len(df.columns)]

            st.dataframe(df, use_container_width=True)
        else:
            st.info("No call logs yet")
    else:
        st.error(f"Failed to fetch call logs (status {res.status_code})")

except Exception as e:
    st.error(f"Error fetching call logs: {e}")
