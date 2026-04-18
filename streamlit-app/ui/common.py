"""
common.py — legacy helpers kept for backward compatibility.
The primary design system is ui/Theme.py.
"""

import math
import streamlit as st

ACCENT      = "#2DD4BF"
ACCENT_SOFT = "#134E4A"
TEXT_MUTED  = "#64748B"
SURFACE     = "#1E293B"
BORDER      = "#334155"

_THEME_KEY = "_ledgerspy_common_theme_v2"


def apply_page_theme() -> None:
    """Apply dark base theme. Called once from app.py before page routing."""
    if st.session_state.get(_THEME_KEY):
        return
    st.session_state[_THEME_KEY] = True

    # Delegate to the canonical Theme.py injector
    try:
        from ui.Theme import inject_global_css
        inject_global_css()
    except ImportError:
        pass  # Theme.py will inject on first render


def render_hero(title: str, subtitle: str, kicker: str = "LedgerSpy") -> None:
    apply_page_theme()
    st.markdown(
        f"""
        <div style='background:#1E293B;border:1px solid #334155;border-radius:22px;
        padding:1.3rem 1.4rem;box-shadow:0 12px 36px rgba(0,0,0,0.4);margin-bottom:1rem'>
            <div style='color:#2DD4BF;text-transform:uppercase;letter-spacing:0.08em;
            font-size:0.82rem;font-weight:700;margin-bottom:0.35rem'>{kicker}</div>
            <div style='font-size:2.4rem;font-weight:800;color:#F1F5F9;margin:0'>{title}</div>
            <div style='color:#CBD5E1;font-size:1.05rem;margin-top:0.45rem;line-height:1.6'>{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(message: str, hint: str | None = None) -> None:
    body = message if hint is None else f"{message}<br><span style='color:{TEXT_MUTED}'>{hint}</span>"
    st.markdown(
        f"""
        <div style='background:{SURFACE};border:1px solid {BORDER};border-radius:14px;
        padding:2rem;text-align:center;color:#F1F5F9'>
            <div style='font-size:1.05rem;font-weight:700;margin-bottom:0.3rem'>Nothing to show yet</div>
            <div style='color:{TEXT_MUTED}'>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_badge(text: str, tone: str = "neutral") -> None:
    palette = {
        "high":    ("#450A0A", "#F87171"),
        "medium":  ("#451A03", "#FCD34D"),
        "low":     ("#052E16", "#4ADE80"),
        "neutral": ("#1E293B", "#94A3B8"),
    }
    bg, fg = palette.get(tone, palette["neutral"])
    st.markdown(
        f"<span style='display:inline-block;background:{bg};color:{fg};"
        f"border-radius:6px;padding:3px 10px;font-size:0.85rem;font-weight:700'>{text}</span>",
        unsafe_allow_html=True,
    )


def safe_percent(value: float | int | None) -> float:
    try:
        numeric = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(100.0, numeric))


def safe_number(value: object, default: float = 0.0) -> float:
    try:
        numeric = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return numeric if math.isfinite(numeric) else default
