import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# 🔥 CHANGE THIS to your Render URL
BASE_URL = "https://clinic-system-m69l.onrender.com"

st.set_page_config(
    page_title="Apollo Clinic Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    /* ===== GLOBAL ===== */
    .stApp {
        background: #0f1117;
    }

    section[data-testid="stSidebar"] {
        background: #161b22;
    }

    /* ===== TOP BAR ===== */
    .top-bar {
        background: linear-gradient(135deg, #1e3a5f 0%, #1a1a2e 100%);
        border-radius: 16px;
        padding: 30px 40px;
        margin-bottom: 30px;
        border: 1px solid #2d3748;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .top-bar h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }

    .top-bar p {
        margin: 5px 0 0 0;
        color: #94a3b8;
        font-size: 0.95rem;
    }

    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(52, 211, 153, 0.15);
        color: #34d399;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }

    .live-dot {
        width: 8px;
        height: 8px;
        background: #34d399;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.8); }
    }

    /* ===== METRIC CARDS ===== */
    .metric-row {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
    }

    .metric-card {
        flex: 1;
        background: #161b22;
        border: 1px solid #2d3748;
        border-radius: 14px;
        padding: 24px 28px;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }

    .metric-card.blue::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
    .metric-card.green::before { background: linear-gradient(90deg, #10b981, #34d399); }
    .metric-card.purple::before { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }

    .metric-icon {
        width: 42px;
        height: 42px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        margin-bottom: 14px;
    }

    .metric-icon.blue { background: rgba(59, 130, 246, 0.15); }
    .metric-icon.green { background: rgba(16, 185, 129, 0.15); }
    .metric-icon.purple { background: rgba(139, 92, 246, 0.15); }

    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }

    /* ===== SECTION HEADERS ===== */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 30px 0 16px 0;
    }

    .section-header h2 {
        margin: 0;
        font-size: 1.3rem;
        font-weight: 700;
        color: #e2e8f0;
    }

    .section-header .count-badge {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* ===== TABLE CONTAINER ===== */
    .table-container {
        background: #161b22;
        border: 1px solid #2d3748;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 24px;
    }

    .table-container table {
        width: 100%;
        border-collapse: collapse;
    }

    .table-container thead th {
        background: #1c2333;
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 14px 20px;
        text-align: left;
        border-bottom: 1px solid #2d3748;
    }

    .table-container tbody td {
        padding: 14px 20px;
        color: #e2e8f0;
        font-size: 0.92rem;
        border-bottom: 1px solid #1e2736;
    }

    .table-container tbody tr:hover {
        background: rgba(59, 130, 246, 0.05);
    }

    .table-container tbody tr:last-child td {
        border-bottom: none;
    }

    /* ===== STATUS BADGE ===== */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge-confirmed {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }

    .badge-completed {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.25);
    }

    .badge-pending {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.25);
    }

    /* ===== TRANSCRIPT CARD ===== */
    .transcript-card {
        background: #161b22;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
    }

    .transcript-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    .transcript-id {
        font-weight: 700;
        color: #60a5fa;
        font-size: 0.95rem;
    }

    .transcript-time {
        color: #64748b;
        font-size: 0.82rem;
    }

    .transcript-body {
        background: #0d1117;
        border: 1px solid #21262d;
        border-radius: 8px;
        padding: 16px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.82rem;
        color: #c9d1d9;
        line-height: 1.6;
        white-space: pre-wrap;
        max-height: 250px;
        overflow-y: auto;
    }

    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 20px;
        color: #4a5568;
        font-size: 0.85rem;
        margin-top: 30px;
        border-top: 1px solid #2d3748;
    }

    /* ===== EMPTY STATE ===== */
    .empty-state {
        background: #161b22;
        border: 1px dashed #2d3748;
        border-radius: 14px;
        padding: 40px;
        text-align: center;
        color: #64748b;
        font-size: 0.95rem;
    }

    .empty-state .icon {
        font-size: 2rem;
        margin-bottom: 10px;
    }

    /* ===== HIDE STREAMLIT DEFAULTS ===== */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Fix Streamlit expander */
    .streamlit-expanderHeader {
        background: #161b22 !important;
        border: 1px solid #2d3748 !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }

    div[data-testid="stExpander"] {
        border: none !important;
    }

    div[data-testid="stExpander"] details {
        border: none !important;
    }

    .stAlert {
        background: #161b22 !important;
        border: 1px solid #2d3748 !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

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
stats = fetch("/api/stats")

if "error" in stats:
    st.error(f"⚠️ {stats['error']}")
else:
    total_calls = stats.get("total_calls", 0)
    total_bookings = stats.get("total_bookings", 0)
    bookings_today = stats.get("bookings_today", 0)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card blue">
            <div class="metric-icon blue">📞</div>
            <div class="metric-label">Total Calls</div>
            <div class="metric-value">{total_calls}</div>
        </div>
        <div class="metric-card green">
            <div class="metric-icon green">📅</div>
            <div class="metric-label">Total Bookings</div>
            <div class="metric-value">{total_bookings}</div>
        </div>
        <div class="metric-card purple">
            <div class="metric-icon purple">⭐</div>
            <div class="metric-label">Bookings Today</div>
            <div class="metric-value">{bookings_today}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- BOOKINGS ----------------
bookings_data = fetch("/api/bookings")

if "error" in bookings_data:
    st.error(f"⚠️ {bookings_data['error']}")
else:
    bookings = bookings_data.get("bookings", [])
    count = len(bookings)

    st.markdown(f"""
    <div class="section-header">
        <h2>📋 Appointment Bookings</h2>
        <span class="count-badge">{count} records</span>
    </div>
    """, unsafe_allow_html=True)

    if bookings:
        rows_html = ""
        for b in bookings:
            status = b.get("status", "confirmed").lower()
            badge_class = f"badge-{status}" if status in ["confirmed", "pending"] else "badge-confirmed"
            status_display = status.upper()

            rows_html += f"""
            <tr>
                <td style="color: #64748b; font-weight: 600;">#{b.get('id', '')}</td>
                <td style="font-weight: 600;">{b.get('patient_name', 'N/A')}</td>
                <td>{b.get('doctor_name', 'N/A')}</td>
                <td>{b.get('appointment_date', 'N/A')}</td>
                <td>{b.get('appointment_time', 'N/A')}</td>
                <td><span class="badge {badge_class}">{status_display}</span></td>
            </tr>
            """

        st.markdown(f"""
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Patient Name</th>
                        <th>Doctor</th>
                        <th>Date</th>
                        <th>Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">📋</div>
            <div>No bookings yet. Appointments will appear here.</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------- CALL LOGS ----------------
calls_data = fetch("/api/call-logs")

if "error" in calls_data:
    st.error(f"⚠️ {calls_data['error']}")
else:
    calls = calls_data.get("call_logs", [])
    call_count = len(calls)

    st.markdown(f"""
    <div class="section-header">
        <h2>📞 Call Logs</h2>
        <span class="count-badge">{call_count} records</span>
    </div>
    """, unsafe_allow_html=True)

    if calls:
        rows_html = ""
        for c in calls:
            outcome = c.get("outcome", "completed").lower()
            badge_class = f"badge-{outcome}" if outcome in ["completed", "pending"] else "badge-completed"
            outcome_display = outcome.upper()
            duration = c.get("duration_seconds", 0)

            # Format duration
            mins = duration // 60
            secs = duration % 60
            duration_display = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

            rows_html += f"""
            <tr>
                <td style="color: #60a5fa; font-weight: 600;">{c.get('call_id', 'N/A')}</td>
                <td>{c.get('call_started_at', 'N/A')}</td>
                <td>{duration_display}</td>
                <td><span class="badge {badge_class}">{outcome_display}</span></td>
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
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # Transcripts
        st.markdown("""
        <div class="section-header">
            <h2>💬 Recent Transcripts</h2>
        </div>
        """, unsafe_allow_html=True)

        for c in calls[:5]:
            transcript = c.get("transcript", "")
            call_id = c.get("call_id", "N/A")
            call_time = c.get("call_started_at", "N/A")

            if transcript:
                st.markdown(f"""
                <div class="transcript-card">
                    <div class="transcript-header">
                        <span class="transcript-id">🎙️ Call {call_id}</span>
                        <span class="transcript-time">{call_time}</span>
                    </div>
                    <div class="transcript-body">{transcript}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="transcript-card">
                    <div class="transcript-header">
                        <span class="transcript-id">🎙️ Call {call_id}</span>
                        <span class="transcript-time">{call_time}</span>
                    </div>
                    <div style="color: #64748b; font-size: 0.88rem;">No transcript available</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">📞</div>
            <div>No calls yet. Call logs will appear here.</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown(f"""
<div class="footer">
    🔄 Auto-refresh every 10 seconds &nbsp;•&nbsp; Last updated: {datetime.now().strftime("%I:%M:%S %p")} &nbsp;•&nbsp; Apollo Clinic AI System
</div>
""", unsafe_allow_html=True)

# ---------------- AUTO REFRESH ----------------
time.sleep(10)
st.rerun()
