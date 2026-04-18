import streamlit as st

def apply_global_theme():
    st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #0e1117;
        color: #e6edf3;
    }
    
    /* Metrics / KPIs styled as cards */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #2a2f36;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] > div {
        color: #00c2ff !important;
        font-weight: 700;
        font-size: 2.2rem;
    }
    div[data-testid="stMetricLabel"] > div > div > p {
        color: #8b949e !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* DataFrame styling wrapper to look like a card */
    div[data-testid="stDataFrame"] {
        background-color: #161b22;
        border: 1px solid #2a2f36;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #2a2f36;
    }
    
    /* Expander / Headers */
    h1, h2, h3 {
        color: #e6edf3 !important;
    }
    
    /* Default simple card matching the injected UI */
    .card { 
        background-color: #161b22; 
        border: 1px solid #2a2f36; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 1rem; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
    }
    .card h3 { 
        color: #00c2ff; 
        font-weight: 600; 
        font-size: 1.2rem; 
        margin-top: 0; 
        margin-bottom: 0.5rem; 
        border-bottom: 1px solid #2a2f36; 
        padding-bottom: 0.5rem; 
    }
    .card p { 
        color: #8b949e; 
        font-size: 0.9rem; 
        margin: 0; 
    }
    
    /* Code blocks (Memo) */
    .mono-block { 
        font-family: 'Courier New', monospace; 
        background-color: #0d1117; 
        border: 1px solid #30363d; 
        padding: 20px; 
        border-radius: 8px; 
        color: #79c0ff; 
        white-space: pre-wrap; 
        font-size: 0.95rem; 
        line-height: 1.5; 
    }
    </style>
    """, unsafe_allow_html=True)
