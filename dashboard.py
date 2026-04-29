import streamlit as st
import requests
import pandas as pd

BASE_URL = "https://clinic-system-m69l.onrender.com"

st.set_page_config(page_title="Apollo Clinic Dashboard", layout="wide")
st.title("Apollo Clinic Dashboard")

# -------- BOOKINGS --------
st.header("Bookings")

try:
    res = requests.get(f"{BASE_URL}/bookings", timeout=10)

    if res.status_code == 200:
        data = res.json().get("bookings", [])
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No bookings yet")
    else:
        st.error(f"Error: {res.status_code}")
except Exception as e:
    st.error(f"Connection error: {e}")

# -------- CALL LOGS --------
st.header("Call Logs")

try:
    res = requests.get(f"{BASE_URL}/calls", timeout=10)

    if res.status_code == 200:
        data = res.json().get("calls", [])
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No call logs yet")
    else:
        st.error(f"Error: {res.status_code}")
except Exception as e:
    st.error(f"Connection error: {e}")
