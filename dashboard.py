import streamlit as st
import requests
import time
from datetime import datetime
import html

BASE_URL = "https://clinic-system-m69l.onrender.com"

st.set_page_config(
    page_title="Apollo Clinic Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- MODERN CSS ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    * { 
        font-family: 'Inter', sans-serif; 
        box-sizing: border-box; 
    }

    .stApp {
        background: #0a0e17;
        min-height: 100vh;
    }

    #MainMenu, footer, header { display: none !important; }
    
    .block-container {
        padding: 2rem 2.5rem !important;
        max-width: 100% !important;
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background:
            radial-gradient(ellipse at 20% 20%, rgba(102, 126, 234, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(118, 75, 162, 0.08) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    .topnav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 22px 36px;
        margin-bottom: 32px;
        box-shadow: 0 4px 30px rgba(0,0,0,0.5);
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .brand-icon {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    .brand-text h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        line-height: 1;
    }

    .brand-text p {
        margin: 4px 0 0 0;
        font-size: 0.8rem;
        color: rgba(255,255,255,0.45);
        font-weight: 400;
    }

    .nav-right {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .time-pill {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 8px 16px;
        font-size: 0.82rem;
        color: rgba(255,255,255,0.5);
        font-weight: 500;
    }

    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(52, 211, 153, 0.12);
        color: #34d399;
        padding: 8px 16px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        border: 1px solid rgba(52, 211, 153, 0.25);
    }

    .live-dot {
        width: 7px;
        height: 7px;
        background: #34d399;
        border-radius: 50%;
        animation: livePulse 1.5s ease-in-out infinite;
        box-shadow: 0 0 10px #34d399;
    }

    @keyframes livePulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.4); opacity: 0.6; }
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 22px;
        margin-bottom: 32px;
    }

    .metric-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 30px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: rgba(255,255,255,0.15);
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    .metric-card.blue { border-top: 3px solid #3b82f6; }
    .metric-card.green { border-top: 3px solid #10b981; }
    .metric-card.purple { border-top: 3px solid #8b5cf6; }

    .metric-glow {
        position: absolute;
        top: -30px;
        right: -30px;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        opacity: 0.08;
        filter: blur(40px);
    }

    .metric-card.blue .metric-glow { background: #3b82f6; }
    .metric-card.green .metric-glow { background: #10b981; }
    .metric-card.purple .metric-glow { background: #8b5cf6; }

    .metric-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 22px;
    }

    .metric-icon-wrap {
        width: 46px;
        height: 46px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
    }

    .metric-card.blue .metric-icon-wrap { background: rgba(59,130,246,0.12); }
    .metric-card.green .metric-icon-wrap { background: rgba(16,185,129,0.12); }
    .metric-card.purple .metric-icon-wrap { background: rgba(139,92,246,0.12); }

    .metric-trend {
        font-size: 0.72rem;
        font-weight: 600;
        padding: 5px 10px;
        border-radius: 8px;
        background: rgba(52,211,153,0.12);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.2);
    }

    .metric-value {
        font-size: 3rem;
        font-weight: 900;
        color: #ffffff;
        line-height: 1;
        margin-bottom: 8px;
        letter-spacing: -2px;
    }

    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: rgba(255,255,255,0.4);
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }

    .section-wrap {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 26px;
    }

    .section-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 22px 30px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.02);
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .section-title-bar {
        width: 3px;
        height: 24px;
        border-radius: 2px;
    }

    .section-title-bar.blue { background: linear-gradient(180deg, #3b82f6, #60a5fa); }
    .section-title-bar.green { background: linear-gradient(180deg, #10b981, #34d399); }
    .section-title-bar.purple { background: linear-gradient(180deg, #8b5cf6, #a78bfa); }

    .section-title h2 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 700;
        color: rgba(255,255,255,0.95);
    }

    .count-badge {
        background: rgba(99,102,241,0.12);
        color: #818cf8;
        padding: 6px 14px;
        border-radius: 10px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: 1px solid rgba(99,102,241,0.25);
    }

    .data-table {
        width: 100%;
        border-collapse: collapse;
    }

    .data-table thead th {
        background: rgba(0,0,0,0.25);
        color: rgba(255,255,255,0.4);
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        padding: 16px 30px;
        text-align: left;
    }

    .data-table tbody td {
        padding: 18px 30px;
        color: rgba(255,255,255,0.85);
        font-size: 0.9rem;
        font-weight: 500;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    .data-table tbody tr:last-child td {
        border-bottom: none;
    }

    .data-table tbody tr {
        transition: background 0.15s ease;
    }

    .data-table tbody tr:hover {
        background: rgba(102,126,234,0.06);
    }

    .id-cell {
        color: rgba(255,255,255,0.25) !important;
        font-size: 0.8rem !important;
        font-family: monospace;
    }

    .name-cell {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    .call-id-cell {
        color: #818cf8 !important;
        font-family: monospace;
        font-size: 0.85rem !important;
    }

    .duration-cell {
        color: #60a5fa !important;
        font-weight: 600 !important;
    }

    .time-cell {
        color: rgba(255,255,255,0.45) !important;
        font-size: 0.84rem !important;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 13px;
        border-radius: 8px;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .badge::before {
        content: '';
        width: 5px;
        height: 5px;
        border-radius: 50%;
    }

    .badge-confirmed {
        background: rgba(16,185,129,0.12);
        color: #34d399;
        border: 1px solid rgba(16,185,129,0.25);
    }

    .badge-confirmed::before { background: #34d399; }

    .badge-completed {
        background: rgba(59,130,246,0.12);
        color: #60a5fa;
        border: 1px solid rgba(59,130,246,0.25);
    }

    .badge-completed::before { background: #60a5fa; }

    .transcript-list {
        padding: 24px 30px;
    }

    .transcript-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        margin-bottom: 16px;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .transcript-card:hover {
        border-color: rgba(129,140,248,0.35);
        box-shadow: 0 4px 20px rgba(129,140,248,0.1);
    }

    .transcript-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 22px;
        background: rgba(0,0,0,0.2);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .transcript-id {
        font-weight: 700;
        color: #818cf8;
        font-size: 0.88rem;
        font-family: monospace;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .transcript-time {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.3);
        font-weight: 500;
    }

    .transcript-body {
        padding: 20px 22px;
        font-family: monospace;
        font-size: 0.82rem;
        color: rgba(255,255,255,0.7);
        line-height: 1.9;
        white-space: pre-wrap;
        max-height: 300px;
        overflow-y: auto;
        background: rgba(0,0,0,0.15);
    }

    .transcript-body::-webkit-scrollbar { width: 5px; }
    .transcript-body::-webkit-scrollbar-track { background: transparent; }
    .transcript-body::-webkit-scrollbar-thumb {
        background: rgba(102,126,234,0.5);
        border-radius: 4px;
    }

    .empty-state {
        padding: 70px 20px;
        text-align: center;
    }

    .empty-icon {
        font-size: 2.8rem;
        margin-bottom: 14px;
        opacity: 0.2;
    }

    .empty-text {
        color: rgba(255,255,255,0.25);
        font-size: 0.92rem;
        font-weight: 500;
    }

    .footer {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        padding: 26px;
        color: rgba(255,255,255,0.2);
        font-size: 0.8rem;
        font-weight: 500;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 16px;
    }

    .footer-dot {
        width: 3px;
        height: 3px;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
    }

    .stAlert {
        background: rgba(239,68,68,0.08) !important;
        border: 1px solid rgba(239,68,68,0.2) !important;
        border-radius: 14px !important;
        color: #fca5a5 !important;
        padding: 16px 20px !important;
    }

    @media (max-width: 768px) {
        .metric-grid { grid-template-columns: 1fr; }
        .topnav { flex-direction: column; gap: 18px; }
        .block-container { padding: 1.5rem !important; }
        .metric-value { font-size: 2.2rem; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------- FETCH FUNCTION ----------------
def fetch(endpoint):
    try:
        res = requests.get(f"{BASE_URL}{endpoint}", timeout=8)
        if res.status_code == 200:
            return res.json()
        else:
            return {"error": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# ---------------- HEADER ----------------
current_time = datetime.now().strftime("%b %d, %Y • %I:%M %p")

st.markdown(f"""
<div class="topnav">
    <div class="brand">
        <div class="brand-icon">🏥</div>
        <div class="brand-text">
            <h1>Apollo Clinic</h1>
            <p>AI-Powered Management Dashboard</p>
        </div>
    </div>
    <div class="nav-right">
        <div class="time-pill">📅 {current_time}</div>
        <div class="live-badge">
            <span class="live-dot"></span> LIVE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- STATS SECTION ----------------
stats = fetch("/api/stats")

if "error" in stats:
    st.error(f"⚠️ Failed to load stats: {stats['error']}")
else:
    total_calls = stats.get("total_calls", 0)
    total_bookings = stats.get("total_bookings", 0)
    bookings_today = stats.get("bookings_today", 0)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card blue">
            <div class="metric-glow"></div>
            <div class="metric-top">
                <div class="metric-icon-wrap">📞</div>
                <div class="metric-trend">↑ Active</div>
            </div>
            <div class="metric-value">{total_calls}</div>
            <div class="metric-label">Total Calls</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card green">
            <div class="metric-glow"></div>
            <div class="metric-top">
                <div class="metric-icon-wrap">📅</div>
                <div class="metric-trend">↑ Growing</div>
            </div>
            <div class="metric-value">{total_bookings}</div>
            <div class="metric-label">Total Bookings</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card purple">
            <div class="metric-glow"></div>
            <div class="metric-top">
                <div class="metric-icon-wrap">⭐</div>
                <div class="metric-trend">↑ Today</div>
            </div>
            <div class="metric-value">{bookings_today}</div>
            <div class="metric-label">Bookings Today</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------- BOOKINGS SECTION ----------------
bookings_data = fetch("/api/bookings")

if "error" not in bookings_data:
    bookings = bookings_data.get("bookings", [])

    st.markdown(f"""
    <div class="section-wrap">
        <div class="section-head">
            <div class="section-title">
                <div class="section-title-bar green"></div>
                <h2>📋 Appointment Bookings</h2>
            </div>
            <span class="count-badge">{len(bookings)} records</span>
        </div>
    """, unsafe_allow_html=True)

    if bookings:
        rows_html = ""
        for b in bookings:
            status = html.escape((b.get('status') or 'confirmed').upper())
            patient_name = html.escape(b.get('patient_name', '—'))
            doctor_name = html.escape(b.get('doctor_name', '—'))
            appointment_date = html.escape(b.get('appointment_date', '—'))
            appointment_time = html.escape(b.get('appointment_time', '—'))
            
            rows_html += f"""
            <tr>
                <td class="id-cell">#{b.get('id', '')}</td>
                <td class="name-cell">{patient_name}</td>
                <td>{doctor_name}</td>
                <td class="time-cell">{appointment_date}</td>
                <td class="time-cell">{appointment_time}</td>
                <td><span class="badge badge-confirmed">{status}</span></td>
            </tr>
            """

        st.markdown(f"""
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📋</div>
            <div class="empty-text">No bookings yet — appointments will appear here</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------- CALL LOGS SECTION ----------------
calls_data = fetch("/api/call-logs")

if "error" not in calls_data:
    calls = calls_data.get("call_logs", [])

    st.markdown(f"""
    <div class="section-wrap">
        <div class="section-head">
            <div class="section-title">
                <div class="section-title-bar blue"></div>
                <h2>📞 Call Logs</h2>
            </div>
            <span class="count-badge">{len(calls)} records</span>
        </div>
    """, unsafe_allow_html=True)

    if calls:
        rows_html = ""
        for c in calls:
            call_id = html.escape(c.get("call_id") or "N/A")
            started_at = html.escape(c.get("call_started_at") or "—")
            duration = c.get("duration_seconds") or 0
            outcome = html.escape((c.get("outcome") or "completed").upper())

            mins = duration // 60
            secs = duration % 60
            duration_display = f"{mins}m {secs}s" if mins else f"{secs}s"

            rows_html += f"""
            <tr>
                <td class="call-id-cell">{call_id}</td>
                <td class="time-cell">{started_at}</td>
                <td class="duration-cell">{duration_display}</td>
                <td><span class="badge badge-completed">{outcome}</span></td>
            </tr>
            """

        st.markdown(f"""
        <table class="data-table">
            <thead>
                <tr>
                    <th>Call ID</th>
                    <th>Started At</th>
                    <th>Duration</th>
                    <th>Outcome</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)

        # ---------------- TRANSCRIPTS SECTION ----------------
        st.markdown(f"""
        <div class="section-wrap">
            <div class="section-head">
                <div class="section-title">
                    <div class="section-title-bar purple"></div>
                    <h2>💬 Call Transcripts (Full Conversations)</h2>
                </div>
                <span class="count-badge">Last {min(10, len(calls))}</span>
            </div>
            <div class="transcript-list">
        """, unsafe_allow_html=True)

        for c in calls[:10]:
            transcript = c.get("transcript") or "No transcript available."
            call_id = html.escape(c.get("call_id") or "—")
            started_at = html.escape(c.get("call_started_at") or "—")

            # Properly escape transcript content
            transcript_escaped = html.escape(str(transcript))

            st.markdown(f"""
            <div class="transcript-card">
                <div class="transcript-header">
                    <span class="transcript-id">🎙️ {call_id}</span>
                    <span class="transcript-time">{started_at}</span>
                </div>
                <div class="transcript-body">{transcript_escaped}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📞</div>
            <div class="empty-text">No calls yet — call logs will appear here</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown(f"""
<div class="footer">
    <span class="footer-dot"></span>
    <span>Last updated {datetime.now().strftime("%H:%M:%S")}</span>
    <span class="footer-dot"></span>
    <span>Apollo Clinic AI System</span>
</div>
""", unsafe_allow_html=True)

# ---------------- AUTO REFRESH ----------------
time.sleep(30)
st.rerun()
