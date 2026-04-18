import streamlit as st

def render_integrity():
    st.markdown('''<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Aurora Background */
    .stApp { 
        background: radial-gradient(circle at 50% 50%, #1a1f35 0%, #0e1117 100%);
        color: #e6edf3; 
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide default sidebar radio buttons to make them look like menu items */
    div.stRadio > div { background: transparent; gap: 8px; }
    div.stRadio > label { display: none; }
    div.stRadio div[role="radiogroup"] > label {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 12px 16px;
        transition: all 0.3s ease;
    }
    div.stRadio div[role="radiogroup"] > label:hover {
        background: rgba(0, 194, 255, 0.1);
        border-color: #00c2ff;
        box-shadow: 0 0 15px rgba(0, 194, 255, 0.2);
        transform: translateX(5px);
    }
    div.stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(90deg, rgba(0,194,255,0.2) 0%, rgba(0,0,0,0) 100%);
        border-left: 4px solid #00c2ff;
    }

    /* Target Streamlit Metrics & Dataframes - The Bento Boxes */
    [data-testid="stMetric"], [data-testid="stDataFrame"] {
        background: rgba(20, 25, 35, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stMetric"]:hover, [data-testid="stDataFrame"]:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 40px rgba(0, 194, 255, 0.15);
        border-color: rgba(0, 194, 255, 0.4);
    }
    
    /* Adds a subtle holographic sweep across cards on hover */
    [data-testid="stMetric"]::before {
        content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.05), transparent);
        transform: skewX(-20deg); transition: 0.5s;
    }
    [data-testid="stMetric"]:hover::before { left: 150%; }

    [data-testid="stMetricLabel"] > div > div > p { color: #a1aab5 !important; font-weight: 600; }
    [data-testid="stMetricValue"] > div {
        color: #fff !important; 
        font-weight: 700; 
        text-shadow: 0 0 20px rgba(0,194,255,0.6);
    }

    /* Custom Headers (H1, H2) with glow */
    h1, h2, h3 { color: #ffffff !important; letter-spacing: -0.02em; }
    h3 { text-shadow: 0 0 10px rgba(255,255,255,0.2); }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00c2ff 0%, #0077ff 100%);
        color: white; border: none; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,194,255,0.3);
        transition: all 0.2s;
    }
    .stButton > button:hover { transform: scale(1.05); box-shadow: 0 6px 20px rgba(0,194,255,0.5); }
    </style>''', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3>Data Integrity Dashboard</h3>
        <p>Data quality metrics and readiness</p>
    </div>
    """, unsafe_allow_html=True)
    
    readiness = st.session_state.get("readiness")
    if not readiness:
        st.info("No data available.")
        return
        
    score = readiness.get('score', 0.0)
    null_pct = readiness.get('null_pct', readiness.get('nulls', 0.0))
    dup_pct = readiness.get('dup_pct', readiness.get('duplicates', 0.0))
    cols = readiness.get('col_count', readiness.get('columns', 'N/A'))
    
    with st.container():
        st.metric("Data Quality Score", f"{score:.1f}%")
        
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Missing Values", f"{null_pct:.2f}%")
        with col2:
            st.metric("Duplicate Rows", f"{dup_pct:.2f}%")
        with col3:
            st.metric("Column Count", cols)
