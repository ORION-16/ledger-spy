"""
LedgerSpy Design System — Dark Theme
Single source of truth for visual tokens, Plotly chart layouts,
and reusable Streamlit UI helper functions.
"""

import streamlit as st

# ── Colour palette ─────────────────────────────────────────────────────────────
C_BG          = "#0F172A"
C_SURFACE     = "#1E293B"
C_SURFACE2    = "#273449"
C_BORDER      = "#334155"
C_BORDER_MED  = "#475569"

C_TEXT_PRIMARY   = "#F1F5F9"
C_TEXT_SECONDARY = "#CBD5E1"
C_TEXT_MUTED     = "#64748B"

C_TEAL     = "#2DD4BF"
C_TEAL_LT  = "#134E4A"
C_SLATE    = "#94A3B8"

C_RED      = "#F87171"
C_RED_LT   = "#450A0A"
C_AMBER    = "#FCD34D"
C_AMBER_LT = "#451A03"
C_GREEN    = "#4ADE80"
C_GREEN_LT = "#052E16"
C_BLUE     = "#60A5FA"
C_BLUE_LT  = "#1E3A5F"
C_PURPLE   = "#A78BFA"
C_PURPLE_LT= "#2E1065"

CHART_FONT   = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
CHART_COLORS = [C_TEAL, C_BLUE, C_PURPLE, C_AMBER, C_RED, C_GREEN]

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#1E293B",
    font=dict(family=CHART_FONT, color=C_TEXT_SECONDARY, size=15),
    title_font=dict(family=CHART_FONT, color=C_TEXT_PRIMARY, size=17),
    xaxis=dict(
        gridcolor="#334155",
        linecolor="#475569",
        zerolinecolor="#334155",
        tickfont=dict(color=C_TEXT_MUTED, size=13),
        title_font=dict(color=C_TEXT_SECONDARY, size=14),
    ),
    yaxis=dict(
        gridcolor="#334155",
        linecolor="#475569",
        zerolinecolor="#334155",
        tickfont=dict(color=C_TEXT_MUTED, size=13),
        title_font=dict(color=C_TEXT_SECONDARY, size=14),
    ),
    legend=dict(
        bgcolor="rgba(30,41,59,0.9)",
        bordercolor=C_BORDER,
        borderwidth=1,
        font=dict(color=C_TEXT_SECONDARY, size=13),
    ),
    hoverlabel=dict(
        bgcolor=C_SURFACE,
        bordercolor=C_BORDER_MED,
        font=dict(family=CHART_FONT, color=C_TEXT_PRIMARY, size=13),
    ),
    margin=dict(l=16, r=16, t=32, b=16),
)


def risk_color(level: str) -> str:
    v = str(level).strip().lower()
    if v == "high":   return C_RED
    if v == "medium": return C_AMBER
    return C_GREEN


def risk_bg(level: str) -> str:
    v = str(level).strip().lower()
    if v == "high":   return C_RED_LT
    if v == "medium": return C_AMBER_LT
    return C_GREEN_LT


# ── Global CSS (injected once per session via a flag in session_state) ─────────
_CSS_KEY = "_ledgerspy_css_v5"


def inject_global_css():
    if st.session_state.get(_CSS_KEY):
        return
    st.session_state[_CSS_KEY] = True

    st.markdown(
        """
<style>
/* ── Reset & root ───────────────────────────────────────────────────── */
:root { color-scheme: dark; }

html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    font-size: 16px !important;
    color: #F1F5F9 !important;
}

/* ── App background ─────────────────────────────────────────────────── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
section.main > div.block-container {
    background-color: #0F172A !important;
    background-image: none !important;
    color: #F1F5F9 !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1280px !important;
}

/* ── Sidebar ────────────────────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background-color: #0B1120 !important;
    border-right: 1px solid #1E293B !important;
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #F1F5F9 !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 1rem !important; padding: 0.45rem 0 !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.82rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748B !important;
    margin-bottom: 0.35rem !important;
}

/* ── Typography — global, cannot be overridden per-page ─────────────── */
p, li, div, span, td, th,
.stMarkdown, .stCaption, .stText,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    font-size: 1rem !important;
    color: #F1F5F9 !important;
    line-height: 1.75 !important;
}

h1 { font-size: 2.4rem !important; font-weight: 800 !important; color: #F1F5F9 !important; }
h2 { font-size: 1.7rem !important; font-weight: 700 !important; color: #F1F5F9 !important; }
h3 { font-size: 1.3rem !important; font-weight: 700 !important; color: #F1F5F9 !important; }
h4 { font-size: 1.1rem !important; font-weight: 600 !important; color: #CBD5E1 !important; }

/* ── Metrics ────────────────────────────────────────────────────────── */
[data-testid="stMetric"],
[data-testid="metric-container"] {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 18px !important;
    padding: 1rem 1.1rem !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35) !important;
}
[data-testid="stMetricLabel"],
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: #64748B !important;
}
[data-testid="stMetricValue"],
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #F1F5F9 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.9rem !important; }

/* ── Buttons ────────────────────────────────────────────────────────── */
.stButton > button,
.stDownloadButton > button {
    border-radius: 999px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    padding: 0.8rem 1.05rem !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 28px rgba(0,0,0,0.45) !important;
}
.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background-color: #0D9488 !important;
    border-color: #0D9488 !important;
    color: #FFFFFF !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #0F766E !important;
    border-color: #0F766E !important;
}
.stButton > button[kind="secondary"],
.stDownloadButton > button[kind="secondary"] {
    border-color: #334155 !important;
    color: #CBD5E1 !important;
    background-color: #1E293B !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #475569 !important;
    background-color: #273449 !important;
}

/* ── DataFrames ─────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #334155 !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    background: #1E293B !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3) !important;
}
[data-testid="stDataFrame"] * { font-size: 0.95rem !important; color: #F1F5F9 !important; }

/* ── Expanders ──────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #334155 !important;
    border-radius: 16px !important;
    background: #1E293B !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25) !important;
}
[data-testid="stExpander"] summary {
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: #F1F5F9 !important;
    padding: 1rem 1.2rem !important;
}

/* ── Inputs ─────────────────────────────────────────────────────────── */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
div[data-baseweb="select"] > div,
.stDateInput input {
    border-radius: 12px !important;
    border-color: #334155 !important;
    background: #1E293B !important;
    color: #F1F5F9 !important;
    font-size: 1rem !important;
}

/* ── File uploader ──────────────────────────────────────────────────── */
[data-testid="stFileUploader"] section {
    background: #1E293B !important;
    border: 1px dashed #475569 !important;
    border-radius: 18px !important;
}

/* ── Alerts ─────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 14px !important;
    font-size: 1rem !important;
    border-width: 1px !important;
    background: #1E293B !important;
}
.stSuccess { background: #052E16 !important; border-color: #166534 !important; }
.stError   { background: #450A0A !important; border-color: #991B1B !important; }
.stWarning { background: #451A03 !important; border-color: #92400E !important; }
.stInfo    { background: #1E3A5F !important; border-color: #1D4ED8 !important; }

/* ── Dividers & HR ──────────────────────────────────────────────────── */
hr { border-color: #334155 !important; margin: 24px 0 !important; }

/* ── Progress bar ───────────────────────────────────────────────────── */
[data-testid="stProgressBar"] > div > div { background-color: #0D9488 !important; }

/* ── Tabs ───────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tab"] {
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: #64748B !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #2DD4BF !important;
    border-bottom-color: #2DD4BF !important;
}

/* ── Tables ─────────────────────────────────────────────────────────── */
[data-testid="stTable"] table { background: #1E293B !important; color: #F1F5F9 !important; }

/* ── Custom component classes ───────────────────────────────────────── */
.ledger-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 22px;
    padding: 1.3rem 1.4rem;
    box-shadow: 0 12px 36px rgba(0,0,0,0.4);
    margin-bottom: 1.2rem;
}
.ledger-section-title {
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: #64748B !important;
    margin-bottom: 0.55rem !important;
}
.ledger-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 999px;
    padding: 0.35rem 0.85rem;
    margin: 0.15rem;
    font-size: 0.9rem !important;
}
.ledger-chip strong { color: #F1F5F9; }

/* Radio buttons dark */
.stRadio > div { gap: 4px !important; }
.stRadio label span { color: #CBD5E1 !important; font-size: 0.97rem !important; }

/* Caption */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #64748B !important;
    font-size: 0.88rem !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


# ── UI helpers ─────────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = ""):
    inject_global_css()
    html = (
        f"<div class='ledger-card'>"
        f"<div style='margin-bottom:0.6rem'>"
        f"<div style='font-size:0.78rem;font-weight:700;letter-spacing:0.14em;"
        f"text-transform:uppercase;color:{C_TEAL};margin-bottom:0.7rem'>Overview</div>"
        f"<h1 style='font-size:2.4rem;font-weight:800;color:{C_TEXT_PRIMARY};"
        f"font-family:Inter,sans-serif;margin:0;line-height:1.05'>{title}</h1>"
        f"</div>"
    )
    if subtitle:
        html += (
            f"<p style='font-size:1.05rem;color:{C_TEXT_SECONDARY};margin:0;"
            f"line-height:1.7;max-width:920px'>{subtitle}</p>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.divider()


def section_header(label: str):
    st.markdown(
        f"<p class='ledger-section-title'>{label}</p>",
        unsafe_allow_html=True,
    )


def card_container(content_fn, padding: str = "20px 24px"):
    st.markdown(
        f"<div style='background:{C_SURFACE};border:1px solid {C_BORDER};"
        f"border-radius:12px;padding:{padding};box-shadow:0 4px 16px rgba(0,0,0,0.3);"
        f"margin-bottom:16px'>",
        unsafe_allow_html=True,
    )
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)


def risk_badge(level: str) -> str:
    level = str(level).strip()
    fg = risk_color(level)
    bg = risk_bg(level)
    return (
        f"<span style='display:inline-block;background:{bg};color:{fg};"
        f"border-radius:6px;padding:3px 10px;font-size:0.85rem;font-weight:700;"
        f"font-family:Inter,sans-serif;letter-spacing:0.04em'>{level.upper()}</span>"
    )


def kpi_badge(label: str, value: str, color: str = C_TEAL):
    return (
        f"<span style='display:inline-flex;align-items:center;gap:6px;"
        f"background:{C_SURFACE2};border:1px solid {C_BORDER};border-radius:8px;"
        f"padding:5px 12px;font-size:0.9rem;font-family:Inter,sans-serif'>"
        f"<span style='color:{C_TEXT_MUTED};font-weight:500'>{label}</span>"
        f"<span style='color:{color};font-weight:700'>{value}</span>"
        f"</span>"
    )


def empty_state(icon: str, title: str, body: str):
    st.markdown(
        f"<div class='ledger-card' style='text-align:center;padding:3rem 2rem;'>"
        f"<div style='font-size:46px;margin-bottom:18px'>{icon}</div>"
        f"<p style='font-size:1.25rem;font-weight:700;color:{C_TEXT_PRIMARY};margin:0 0 0.75rem'>{title}</p>"
        f"<p style='font-size:1rem;color:{C_TEXT_SECONDARY};max-width:420px;margin:0 auto;line-height:1.75'>{body}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )


def info_box(text: str):
    st.markdown(
        f"<div style='background:#134E4A;border:1px solid #0F766E;border-radius:10px;"
        f"padding:14px 18px;font-size:1rem;color:{C_TEXT_SECONDARY};line-height:1.65;"
        f"margin:12px 0'>{text}</div>",
        unsafe_allow_html=True,
    )


def memo_box(text: str):
    st.markdown(
        f"<div style='background:#1E293B;border:1px solid {C_BORDER};"
        f"border-left:4px solid {C_TEAL};border-radius:10px;padding:18px 20px;"
        f"font-size:0.95rem;font-family:\"SFMono-Regular\",Consolas,monospace;"
        f"color:{C_TEXT_SECONDARY};line-height:1.75;white-space:pre-wrap'>{text}</div>",
        unsafe_allow_html=True,
    )


def spacer(px: int = 16):
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)
