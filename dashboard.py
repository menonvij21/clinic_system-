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
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Card styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* Headers */
    h1 {
        color: white !important;
        font-weight: 800 !important;
        text-align: center;
        font-size: 3rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        margin-bottom: 2rem !important;
    }
    
    h2, h3 {
        color: white !important;
        font-weight: 700 !important;
        margin-top: 2rem !important;
    }
    
    /* Metric containers */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #667eea !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #4a5568 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* DataFrames */
    .dataframe {
        background: white !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: #2d3748 !important;
    }
    
    /* Info/Error boxes */
    .stAlert {
        border-radius: 10px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Tables */
    thead tr th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 15px !important;
    }
    
    tbody tr:hover {
        background: #f7fafc !important;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .status-confirmed {
        background: #48bb78;
        color: white;
    }
    
    .status-completed {
        background: #4299e1;
        color: white;
    }
    
    /* Caption styling */
    .caption {
        text-align: center;
        color: white !important;
        font-weight: 500;
        margin-top: 2rem;
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    /* Section containers */
    .section-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
    <h1>🏥 Apollo Clinic Dashboard</h1>
""", unsafe_allow_html=True)

# Current time display
current_time = datetime.now().strftime("%B %d, %Y • %I:%M %p")
st.markdown(f"<p style='text-align: center; color: white; font-size: 1.1rem; margin-top: -1rem;'>📅 {current_time}</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

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
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.subheader("📊 Real-Time Statistics")

stats = fetch("/api/stats")

if "error" in stats:
    st.error(f"⚠️ {stats['error']}")
else:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📞 Total Calls", stats.get("total_calls", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📅 Total Bookings", stats.get("total_bookings", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🌟 Bookings Today", stats.get("bookings_today", 0))
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BOOKINGS ----------------
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.subheader("📋 Appointment Bookings")

bookings_data = fetch("/api/bookings")

if "error" in bookings_data:
    st.error(f"⚠️ {bookings_data['error']}")
else:
    bookings = bookings_data.get("bookings", [])

    if bookings:
        df = pd.DataFrame(bookings)
        
        # Add status badges
        if 'status' in df.columns:
            df['status'] = df['status'].apply(
                lambda x: f'<span class="status-badge status-{x.lower()}">{x.upper()}</span>'
            )
        
        # Rename columns for better display
        column_mapping = {
            'id': 'ID',
            'patient_name': 'Patient Name',
            'doctor_name': 'Doctor',
            'appointment_date': 'Date',
            'appointment_time': 'Time',
            'status': 'Status'
        }
        df = df.rename(columns=column_mapping)
        
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("ℹ️ No bookings yet")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALL LOGS ----------------
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.subheader("📞 Call Logs")

calls_data = fetch("/api/call-logs")

if "error" in calls_data:
    st.error(f"⚠️ {calls_data['error']}")
else:
    calls = calls_data.get("call_logs", [])

    if calls:
        df = pd.DataFrame(calls)

        # Rename columns
        column_mapping = {
            'call_id': 'Call ID',
            'call_started_at': 'Started At',
            'duration_seconds': 'Duration (s)',
            'outcome': 'Outcome'
        }
        
        display_df = df.drop(columns=["transcript"]).rename(columns=column_mapping)
        
        # Add outcome badges
        if 'Outcome' in display_df.columns:
            display_df['Outcome'] = display_df['Outcome'].apply(
                lambda x: f'<span class="status-badge status-{x.lower()}">{x.upper()}</span>'
            )
        
        st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        # Expand transcript view
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 💬 Recent Transcripts")
        
        for i, c in enumerate(calls[:5]):
            with st.expander(f"🎙️ Call {c['call_id']} • {c.get('call_started_at', 'N/A')}"):
                if c.get('transcript'):
                    st.code(c['transcript'], language=None)
                else:
                    st.info("No transcript available")
    else:
        st.info("ℹ️ No calls yet")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- AUTO REFRESH ----------------
st.markdown(f"""
    <div class="caption">
        🔄 Auto-refresh every 10 seconds • Last updated: {datetime.now().strftime("%I:%M:%S %p")}
    </div>
""", unsafe_allow_html=True)

time.sleep(10)
st.rerun()
