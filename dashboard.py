import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

BASE_URL = "https://clinic-system-m69l.onrender.com"

st.set_page_config(
    page_title="Apollo Clinic Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# ---------------- HEADER ----------------
current_time = datetime.now().strftime("%B %d, %Y • %I:%M %p")

st.markdown(f"""
<div class="top-bar">
    <div>
        <h1>🏥 Apollo Clinic</h1>
        <p>AI-Powered Clinic Management Dashboard</p>
    </div>
    <div style="text-align: right;">
        <div class="live-badge">
            <span class="live-dot"></span> LIVE
        </div>
        <p style="color: #64748b; font-size: 0.82rem; margin-top: 8px;">📅 {current_time}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- STATS ----------------
stats = fetch("/api/stats")

if "error" in stats:
    st.error(stats["error"])
else:
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card blue">
            <div class="metric-icon blue">📞</div>
            <div class="metric-label">Total Calls</div>
            <div class="metric-value">{stats.get("total_calls", 0)}</div>
        </div>
        <div class="metric-card green">
            <div class="metric-icon green">📅</div>
            <div class="metric-label">Total Bookings</div>
            <div class="metric-value">{stats.get("total_bookings", 0)}</div>
        </div>
        <div class="metric-card purple">
            <div class="metric-icon purple">⭐</div>
            <div class="metric-label">Bookings Today</div>
            <div class="metric-value">{stats.get("bookings_today", 0)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- BOOKINGS ----------------
bookings_data = fetch("/api/bookings")

if "error" not in bookings_data:
    bookings = bookings_data.get("bookings", [])

    st.markdown(f"""
    <div class="section-header">
        <h2>📋 Appointment Bookings</h2>
        <span class="count-badge">{len(bookings)} records</span>
    </div>
    """, unsafe_allow_html=True)

    if bookings:
        rows = ""
        for b in bookings:
            rows += f"""
            <tr>
                <td>#{b.get('id','')}</td>
                <td>{b.get('patient_name','')}</td>
                <td>{b.get('doctor_name','')}</td>
                <td>{b.get('appointment_date','')}</td>
                <td>{b.get('appointment_time','')}</td>
                <td><span class="badge badge-confirmed">{b.get('status','CONFIRMED')}</span></td>
            </tr>
            """

        st.markdown(f"""
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ID</th><th>Patient</th><th>Doctor</th>
                        <th>Date</th><th>Time</th><th>Status</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

# ---------------- CALL LOGS ----------------
calls_data = fetch("/api/call-logs")

if "error" not in calls_data:
    calls = calls_data.get("call_logs", [])

    st.markdown(f"""
    <div class="section-header">
        <h2>📞 Call Logs</h2>
        <span class="count-badge">{len(calls)} records</span>
    </div>
    """, unsafe_allow_html=True)

    if calls:
        rows = ""

        for c in calls:
            # 🔥 FIXED MAPPING (VERY IMPORTANT)
            call_id = c.get("call_id") or c.get("id", "N/A")
            started_at = c.get("call_started_at") or c.get("timestamp", "N/A")
            duration = c.get("duration_seconds", 0)
            outcome = c.get("outcome", "completed")

            # Format duration
            mins = duration // 60
            secs = duration % 60
            duration_display = f"{mins}m {secs}s" if mins else f"{secs}s"

            rows += f"""
            <tr>
                <td>{call_id}</td>
                <td>{started_at}</td>
                <td>{duration_display}</td>
                <td><span class="badge badge-completed">{outcome.upper()}</span></td>
            </tr>
            """

        st.markdown(f"""
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Call ID</th>
                        <th>Started At</th>
                        <th>Duration</th>
                        <th>Outcome</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # ---------------- TRANSCRIPTS ----------------
        st.markdown("""
        <div class="section-header">
            <h2>💬 Recent Transcripts</h2>
        </div>
        """, unsafe_allow_html=True)

        for c in calls[:5]:
            transcript = c.get("transcript") or c.get("agent_response") or "No transcript"
            call_id = c.get("call_id") or c.get("id")

            st.markdown(f"""
            <div class="transcript-card">
                <div class="transcript-header">
                    <span class="transcript-id">Call {call_id}</span>
                </div>
                <div class="transcript-body">{transcript}</div>
            </div>
            """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown(f"""
<div class="footer">
    Auto-refresh every 10 seconds • {datetime.now().strftime("%H:%M:%S")}
</div>
""", unsafe_allow_html=True)

# ---------------- AUTO REFRESH ----------------
time.sleep(10)
st.rerun()
