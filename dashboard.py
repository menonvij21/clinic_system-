```python
import streamlit as st
import requests
import time
from datetime import datetime

BASE_URL = "https://clinic-system-m69l.onrender.com"

st.set_page_config(
    page_title="Apollo Clinic Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- SIMPLE MODERN CSS ----------------
st.markdown("""
<style>
    .stApp {
        background: #0a0e1a;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    #MainMenu, footer, header { display: none !important; }
    .block-container { padding: 0 2rem 2rem 2rem !important; }
    
    /* Header */
    .header {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-left h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .header-left p {
        margin: 4px 0 0 0;
        color: rgba(255,255,255,0.4);
        font-size: 0.85rem;
    }
    
    .header-right {
        display: flex;
        gap: 12px;
        align-items: center;
    }
    
    .time-badge {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 8px 16px;
        border-radius: 10px;
        color: rgba(255,255,255,0.6);
        font-size: 0.82rem;
    }
    
    .live-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(52,211,153,0.1);
        border: 1px solid rgba(52,211,153,0.3);
        padding: 8px 16px;
        border-radius: 10px;
        color: #34d399;
        font-size: 0.78rem;
        font-weight: 700;
    }
    
    .live-dot {
        width: 8px;
        height: 8px;
        background: #34d399;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
    
    /* Metrics */
    .metrics {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .metric {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 24px;
        transition: all 0.3s;
    }
    
    .metric:hover {
        transform: translateY(-2px);
        border-color: rgba(255,255,255,0.15);
    }
    
    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 12px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #fff;
        margin-bottom: 4px;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Sections */
    .section {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        margin-bottom: 20px;
        overflow: hidden;
    }
    
    .section-header {
        padding: 18px 24px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #fff;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .badge {
        background: rgba(99,102,241,0.2);
        color: #818cf8;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.72rem;
        font-weight: 700;
    }
    
    /* Table */
    table {
        width: 100%;
        border-collapse: collapse;
    }
    
    th {
        background: rgba(0,0,0,0.2);
        color: rgba(255,255,255,0.4);
        padding: 14px 20px;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
        text-align: left;
    }
    
    td {
        padding: 14px 20px;
        color: rgba(255,255,255,0.8);
        font-size: 0.88rem;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    
    tr:hover td {
        background: rgba(102,126,234,0.05);
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .status-confirmed {
        background: rgba(16,185,129,0.15);
        color: #34d399;
        border: 1px solid rgba(16,185,129,0.3);
    }
    
    .status-completed {
        background: rgba(59,130,246,0.15);
        color: #60a5fa;
        border: 1px solid rgba(59,130,246,0.3);
    }
    
    /* Transcripts */
    .transcript {
        margin: 12px 20px 20px 20px;
        background: rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        overflow: hidden;
    }
    
    .transcript-header {
        padding: 12px 16px;
        background: rgba(0,0,0,0.3);
        border-bottom: 1px solid rgba(255,255,255,0.06);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .transcript-id {
        color: #818cf8;
        font-weight: 700;
        font-size: 0.85rem;
        font-family: monospace;
    }
    
    .transcript-time {
        color: rgba(255,255,255,0.3);
        font-size: 0.75rem;
    }
    
    .transcript-body {
        padding: 16px;
        font-family: 'Courier New', monospace;
        font-size: 0.82rem;
        color: rgba(255,255,255,0.7);
        line-height: 1.6;
        max-height: 200px;
        overflow-y: auto;
    }
    
    /* Empty */
    .empty {
        padding: 40px;
        text-align: center;
        color: rgba(255,255,255,0.3);
    }
    
    .empty-icon {
        font-size: 2rem;
        margin-bottom: 10px;
        opacity: 0.5;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: rgba(255,255,255,0.2);
        font-size: 0.8rem;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- FETCH ----------------
def fetch(endpoint):
    try:
        res = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        return res.json() if res.status_code == 200 else {"error": f"Error {res.status_code}"}
    except:
        return {"error": "Connection failed"}

# ---------------- HEADER ----------------
current_time = datetime.now().strftime("%b %d, %Y • %I:%M %p")

st.markdown(f"""
<div class="header">
    <div class="header-left">
        <h1>🏥 Apollo Clinic</h1>
        <p>AI-Powered Management Dashboard</p>
    </div>
    <div class="header-right">
        <div class="time-badge">📅 {current_time}</div>
        <div class="live-badge">
            <span class="live-dot"></span> LIVE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- STATS ----------------
stats = fetch("/api/stats")

if "error" in stats:
    st.error(f"⚠️ {stats['error']}")
else:
    total_calls = stats.get("total_calls", 0)
    total_bookings = stats.get("total_bookings", 0)
    bookings_today = stats.get("bookings_today", 0)

    st.markdown(f"""
    <div class="metrics">
        <div class="metric">
            <div class="metric-icon">📞</div>
            <div class="metric-value">{total_calls}</div>
            <div class="metric-label">Total Calls</div>
        </div>
        <div class="metric">
            <div class="metric-icon">📅</div>
            <div class="metric-value">{total_bookings}</div>
            <div class="metric-label">Total Bookings</div>
        </div>
        <div class="metric">
            <div class="metric-icon">⭐</div>
            <div class="metric-value">{bookings_today}</div>
            <div class="metric-label">Bookings Today</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- BOOKINGS ----------------
bookings_data = fetch("/api/bookings")

if "error" not in bookings_data:
    bookings = bookings_data.get("bookings", [])

    st.markdown(f"""
    <div class="section">
        <div class="section-header">
            <h2 class="section-title">📋 Appointments</h2>
            <span class="badge">{len(bookings)} records</span>
        </div>
    """, unsafe_allow_html=True)

    if bookings:
        rows = ""
        for b in bookings:
            status = b.get('status', 'confirmed')
            rows += f"""
            <tr>
                <td>#{b.get('id','')}</td>
                <td><strong>{b.get('patient_name','')}</strong></td>
                <td>{b.get('doctor_name','')}</td>
                <td>{b.get('appointment_date','')}</td>
                <td>{b.get('appointment_time','')}</td>
                <td><span class="status-badge status-confirmed">{status.upper()}</span></td>
            </tr>
            """

        st.markdown(f"""
        <table>
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
            <tbody>{rows}</tbody>
        </table>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty">
            <div class="empty-icon">📋</div>
            <div>No appointments yet</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- CALLS ----------------
calls_data = fetch("/api/call-logs")

if "error" not in calls_data:
    calls = calls_data.get("call_logs", [])

    st.markdown(f"""
    <div class="section">
        <div class="section-header">
            <h2 class="section-title">📞 Call Logs</h2>
            <span class="badge">{len(calls)} records</span>
        </div>
    """, unsafe_allow_html=True)

    if calls:
        rows = ""
        for c in calls:
            call_id = c.get("call_id") or c.get("id", "N/A")
            started_at = c.get("call_started_at") or c.get("timestamp", "N/A")
            duration = c.get("duration_seconds", 0)
            outcome = c.get("outcome", "completed")
            
            mins = duration // 60
            secs = duration % 60
            duration_str = f"{mins}m {secs}s" if mins else f"{secs}s"

            rows += f"""
            <tr>
                <td><strong>{call_id}</strong></td>
                <td>{started_at}</td>
                <td>{duration_str}</td>
                <td><span class="status-badge status-completed">{outcome.upper()}</span></td>
            </tr>
            """

        st.markdown(f"""
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
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Transcripts
        st.markdown("""
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">💬 Transcripts</h2>
                <span class="badge">Last 5</span>
            </div>
        """, unsafe_allow_html=True)

        for c in calls[:5]:
            transcript = c.get("transcript") or c.get("agent_response") or "No transcript"
            call_id = c.get("call_id") or c.get("id", "—")
            time_str = c.get("call_started_at") or "—"

            st.markdown(f"""
            <div class="transcript">
                <div class="transcript-header">
                    <span class="transcript-id">{call_id}</span>
                    <span class="transcript-time">{time_str}</span>
                </div>
                <div class="transcript-body">{transcript}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="empty">
            <div class="empty-icon">📞</div>
            <div>No calls yet</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown(f"""
<div class="footer">
    🔄 Auto-refresh • Updated {datetime.now().strftime("%H:%M:%S")} • Apollo Clinic AI
</div>
""", unsafe_allow_html=True)

# ---------------- REFRESH ----------------
time.sleep(10)
st.rerun()
```

## What I Fixed

| Issue | Solution |
|-------|----------|
| **Broken CSS** | Removed complex pseudo-elements, simplified all styles |
| **@import url()** | Removed Google Fonts import (Streamlit doesn't support it well) |
| **Too many nested divs** | Flattened structure, removed unnecessary wrappers |
| **Animation conflicts** | Removed complex animations, kept only simple pulse |
| **Rendering issues** | Simplified all classes, removed advanced CSS features |
| **Table structure** | Fixed HTML table rendering with proper thead/tbody |
| **Backend mapping** | Kept exact field names: `call_id`, `call_started_at`, `duration_seconds`, `outcome`, `transcript` |

