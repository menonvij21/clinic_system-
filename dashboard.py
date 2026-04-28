import streamlit as st
import sqlite3
import pandas as pd

st.title("Apollo Clinic Dashboard")

conn = sqlite3.connect("clinic.db")

# BOOKINGS
st.subheader("Bookings")
try:
    bookings = pd.read_sql("SELECT * FROM bookings", conn)
    if bookings.empty:
        st.write("No bookings yet")
    else:
        st.dataframe(bookings)
except Exception as e:
    st.error(f"Booking error: {e}")

# CALL LOGS
st.subheader("Call Logs")
try:
    calls = pd.read_sql("SELECT * FROM calls", conn)
    if calls.empty:
        st.write("No calls yet")
    else:
        st.dataframe(calls)
except Exception as e:
    st.error(f"Call error: {e}")