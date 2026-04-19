import streamlit as st

def apply_global_styles():
    st.markdown('''<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Premium Deep Black Background */
    .stApp { 
        background-color: #050505;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(139, 92, 246, 0.05), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(56, 189, 248, 0.05), transparent 25%);
        color: #f3f4f6; 
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Clean up the sidebar */
    [data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #1f1f1f; }
    
    /* Sidebar Links */
    div.stRadio > div { gap: 8px; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-of-type { display: none !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        padding: 14px 18px; /* Balanced left padding */
        background: #111111;
        border: 1px solid #222222;
        border-radius: 10px;
        margin-bottom: 8px; /* Equal vertical spacing */
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: row;
        align-items: center; /* Centered vertically */
        justify-content: flex-start; /* Aligned left */
        width: 100%; /* Consistent width */
        box-sizing: border-box;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        margin: 0;
        font-size: 0.95rem; /* modern slightly larger text */
        display: flex;
        align-items: center;
        gap: 12px; /* space between icon and text */
        width: 100%;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: rgba(139, 92, 246, 0.08);
        border-color: rgba(139, 92, 246, 0.3);
        box-shadow: 0 0 12px rgba(139, 92, 246, 0.15);
    }
    /* Active Glowing Page Link */
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(90deg, rgba(139, 92, 246, 0.15), rgba(56, 189, 248, 0.05));
        border: 1px solid rgba(139, 92, 246, 0.5);
        box-shadow: 0 0 25px rgba(139, 92, 246, 0.3), inset 0 0 12px rgba(139, 92, 246, 0.15);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"]::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0; width: 4px;
        background: #8b5cf6;
        box-shadow: 0 0 12px #8b5cf6, 0 0 20px #8b5cf6;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p {
        color: #ffffff !important;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(139, 92, 246, 0.6);
        letter-spacing: 0.02em;
    }

    /* Column Container fixes for even heights */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
    }
    [data-testid="column"] > div {
        height: 100%;
    }

    /* Target Streamlit Metrics & Dataframes - The Bento Boxes */
    [data-testid="stMetric"], .card {
        background: rgba(18, 18, 18, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.08); /* Smoother, more even borders */
        border-radius: 16px;
        padding: 32px; /* More padding between content and border */
        margin-bottom: 24px; /* Wider spacing between sections */
        box-shadow: 0 4px 24px rgba(0,0,0,0.45);
        transition: all 0.3s ease;
        position: relative;
        height: 100%; /* Force even height */
        display: flex;
        flex-direction: column;
        justify-content: center; /* Center horizontally & vertically */
        box-sizing: border-box;
    }
    /* Top subtle glow edge for cards */
    [data-testid="stMetric"]::before, .card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.3), transparent);
    }
    /* Glows and Gentle Color Change on Hover */
    [data-testid="stMetric"]:hover, .card:hover {
        background: rgba(26, 26, 30, 0.85);
        border-color: rgba(139, 92, 246, 0.3); /* Slightly softer hover border */
        box-shadow: 0 4px 30px rgba(139, 92, 246, 0.25);
    }

    /* KPIs Streamline / Align */
    [data-testid="stMetricLabel"] > div > div > p { 
        color: #9ca3af !important; 
        font-weight: 600; /* Bolded label */
        font-size: 0.9rem; /* Cleaned sizing */
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin: 0;
        text-align: left; /* Align neatly */
    }
    [data-testid="stMetricValue"] > div {
        color: #f3f4f6 !important; 
        font-weight: 800; /* Bigger/bolder numbers */
        font-size: 2.8rem;
        letter-spacing: -0.02em;
        margin-top: 8px;
        line-height: 1;
        text-align: left; /* Align neatly */
    }

    /* Custom Headers - Bigger + bolder, more padding */
    h1, h2, h3 { 
        color: #ffffff !important; 
        letter-spacing: -0.02em; 
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700 !important;
    }
    h1 { font-size: 2.5rem !important; margin-bottom: 2rem !important; }
    h2 { font-size: 2rem !important; margin-bottom: 1.5rem !important; }
    h3 { font-size: 1.5rem !important; padding-bottom: 8px; margin-bottom: 1rem !important; }

    .card h3 {
        color: #e5e7eb;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding-bottom: 16px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .card p { color: #a1a1aa; font-size: 0.95rem; margin: 0; line-height: 1.6; }

    /* Info / Warnings / Alert Boxes styling */
    [data-testid="stAlert"] {
        background: rgba(139, 92, 246, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        padding: 16px;
    }
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
        color: #e5e7eb !important;
        font-weight: 500;
        font-size: 1.05rem;
        margin: 0;
    }

    /* Buttons */
    .stButton > button {
        background: rgba(30, 30, 30, 0.8);
        color: #f3f4f6; 
        border: 1px solid rgba(255,255,255,0.1); 
        border-radius: 8px; 
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover { 
        background: rgba(139, 92, 246, 0.15);
        border-color: rgba(139, 92, 246, 0.5);
        color: #ddd6fe;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
        transform: scale(1) !important;
        margin: 0 !important;
    }
    
    /* Code blocks (Memo) */
    .mono-block {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        background-color: #050505;
        border: 1px solid rgba(139, 92, 246, 0.2);
        padding: 24px;
        border-radius: 12px;
        color: #c4b5fd;
        white-space: pre-wrap;
        font-size: 0.9rem;
        line-height: 1.6;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
    }
    
    /* Beautiful Dataframe overrides */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        margin-top: 1rem;
        background: transparent;
        padding: 0; /* Remove 24px inner padding */
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    [data-testid="stDataFrame"] * {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    [data-testid="stDataFrame"]:hover {
        border-color: rgba(139, 92, 246, 0.4) !important;
        box-shadow: 0 4px 30px rgba(139, 92, 246, 0.2);
    }
    
    .table-header-box {
        background: rgba(18, 18, 18, 0.7);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.08); 
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        margin-bottom: 2rem;
    }
    .table-header-box h3 { margin: 0; color: #e5e7eb; display:flex; align-items: center; gap:8px; }


    
    /* --- MODERN NOTICE BOX (The AFTER image logic) --- */
    
    /* Target the column that contains the .notice-box marker */
    div[data-testid="column"]:has(.notice-box) {
        background: linear-gradient(135deg, #0a0b0e 0%, #161a1d 100%);
        border: 1px solid rgba(34, 197, 94, 0.4) !important;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 8px 32px rgba(34, 197, 94, 0.08), inset 0 0 20px rgba(34, 197, 94, 0.05); /* Green glow border effect */
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
    }
    
    .notice-box {
        margin-bottom: 8px;
    }
    .notice-box-title {
        color: #ffffff;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 8px;
        letter-spacing: -0.01em;
    }
    .notice-box-subtitle {
        color: #9ca3af;
        font-size: 1rem;
        font-weight: 400;
        margin: 0;
    }

    /* Style the file uploader INSIDE this column to lose its own borders and match gracefully! */
    div[data-testid="column"]:has(.notice-box) [data-testid="stFileUploader"] {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0;
        width: 100%;
    }
    
    div[data-testid="column"]:has(.notice-box) [data-testid="stFileUploader"] > section {
        border: 1px dashed rgba(255,255,255,0.1) !important; /* Subtle dotted inner line instead of harsh box */
        background: rgba(0,0,0,0.2) !important;
        border-radius: 12px;
        padding: 24px;
        width: 100%;
    }
    
    /* Upload Button overrides inside our modern box */
    div[data-testid="column"]:has(.notice-box) [data-testid="stFileUploader"] button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        border-radius: 8px;
        padding: 10px 32px;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div[data-testid="column"]:has(.notice-box) [data-testid="stFileUploader"] button:hover {
        background: rgba(34, 197, 94, 0.15) !important;
        border-color: rgba(34, 197, 94, 0.5) !important;
        color: #22c55e !important;
        box-shadow: 0 0 16px rgba(34, 197, 94, 0.2);
    }
    /* Clean up default Streamlit texts in the uploader */
    div[data-testid="column"]:has(.notice-box) [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }
    
    div[data-testid="column"]:has(.notice-box) [data-testid="stFileUploader"] button {
        /* Hide original text "Browse files" */
        color: transparent !important;
        position: relative;
    }

    div[data-testid="column"]:has(.notice-box) [data-testid="stFileUploader"] button::after {
        content: 'Upload';
        color: #ffffff;
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1rem;
        transition: color 0.3s ease;
    }
    
    div[data-testid="column"]:has(.notice-box) [data-testid="stFileUploader"] button:hover::after {
        color: #22c55e;
    }

    /* Small "or drag and drop" under the button if needed? We already have the subtitle in the box! but let's add it near the button as well */
    div[data-testid="column"]:has(.notice-box) [data-testid="stFileUploader"] > section::after {
        content: 'or drag and drop';
        display: block;
        text-align: center;
        color: #6b7280;
        font-size: 0.85rem;
        margin-top: 12px;
    }

    </style>''', unsafe_allow_html=True)
