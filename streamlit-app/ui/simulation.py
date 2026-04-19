"""
ui/simulation.py — Monte Carlo Going Concern Stress Test
Full dedicated section with charts, KPIs, and interpretation.
"""

from ui.styles import apply_global_styles
import streamlit as st
import pandas as pd
import numpy as np


# ── shared helpers ─────────────────────────────────────────────────────────────

def _page_header(icon: str, title: str, subtitle: str) -> None:
    st.markdown(f"""
    <div class="card page-header">
        <h2>{icon} {title}</h2>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def _section(title: str) -> None:
    st.markdown(
        f"<p class='section-header'>{title}</p>",
        unsafe_allow_html=True,
    )


def _risk_badge_html(risk_level: str, risk_color: str) -> str:
    return (
        f"<span style='background:{risk_color}22;color:{risk_color};"
        f"border:1px solid {risk_color}55;border-radius:8px;"
        f"padding:7px 20px;font-size:1rem;font-weight:700;"
        f"letter-spacing:0.04em;display:inline-block'>"
        f"Going-Concern Risk: {risk_level}</span>"
    )


def render_simulation() -> None:
    apply_global_styles()

    _page_header(
        "📈",
        "Monte Carlo Stress Test",
        "Simulates 1,000 independent cash-flow scenarios over 12 months to estimate "
        "the entity's going-concern survival probability.",
    )

    df = st.session_state.get("df")
    if df is None:
        st.info("📂  No dataset loaded. Upload a CSV from the sidebar first.")
        return

    # ── Controls ───────────────────────────────────────────────────────────────
    with st.expander("⚙️  Simulation Settings", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            n_sims = st.slider("Number of simulations", 200, 2000, 1000, step=100)
        with col_b:
            n_months = st.slider("Forecast horizon (months)", 6, 24, 12, step=1)

    btn_col, _ = st.columns([1, 3])
    with btn_col:
        run_clicked = st.button("▶  Run Simulation", type="primary", use_container_width=True)

    if run_clicked:
        st.session_state["mc_result"] = None  # force re-run

    # ── Run / retrieve ─────────────────────────────────────────────────────────
    # ── Audit signal: fetch anomaly rate from session state (Step 2) ──────────
    risk_scores  = st.session_state.get("risk_scores", {})
    anomaly_count = risk_scores.get("anomaly_count", 0)
    total_records = max(risk_scores.get("total", 1), 1)
    anomaly_rate  = anomaly_count / total_records   # fraction, e.g. 0.12 for 12%

    result = st.session_state.get("mc_result")
    if result is None:
        with st.spinner(f"Running {n_sims:,} Monte Carlo simulations over {n_months} months…"):
            try:
                from ml.monte_carlo import monte_carlo_simulation
                result = monte_carlo_simulation(
                    df,
                    n_simulations=n_sims,
                    n_months=n_months,
                    anomaly_rate=anomaly_rate,   # Step 2: audit stress signal
                )
                st.session_state["mc_result"] = result
            except ImportError:
                st.error("❌  `modules/monte_carlo.py` not found. Ensure it's in your project root.")
                return
            except Exception as exc:
                st.error(f"❌  Simulation failed: {exc}")
                return

    if result is None or result.get("survival_probability") is None:
        st.error("❌  Could not run simulation. Ensure your dataset has an `amount` column.")
        return

    prob            = result["survival_probability"]
    risk_level      = result["risk_level"]
    risk_color      = result["risk_color"]
    avg_inc         = result["avg_monthly_income"]
    avg_exp         = result["avg_monthly_expense"]         # stressed
    expense_mult    = result.get("expense_multiplier", 1.0)
    n_ran           = result["n_simulations"]

    # ── KPI strip ──────────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Probability of maintaining positive cash balance over 12 months", f"{prob:.1f}%")
    c2.metric("Simulations Run",           f"{n_ran:,}")
    c3.metric("Avg Monthly Income",        f"$ {avg_inc:,.0f}")
    c4.metric("Avg Monthly Expense (stressed)", f"$ {avg_exp:,.0f}",
              delta=f"{expense_mult:.2f}× multiplier from {anomaly_rate*100:.1f}% anomaly rate",
              delta_color="off")

    # ── Risk verdict ───────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='margin:20px 0 10px'>{_risk_badge_html(risk_level, risk_color)}</div>",
        unsafe_allow_html=True,
    )

    interpretations = {
        "Low":    f"<span style='color:{risk_color}'>✅  Strong going-concern.</span>  "
                  "The entity shows a high likelihood of maintaining positive cash flow "
                  "across simulated scenarios. Continue standard monitoring.",
        "Medium": f"<span style='color:{risk_color}'>⚠️  Moderate uncertainty.</span>  "
                  "Some simulated paths result in negative balances. "
                  "Implement cash-flow controls and review expense projections.",
        "High":   f"<span style='color:{risk_color}'>🔴  Critical risk.</span>  "
                  "The majority of simulated scenarios result in insolvency within the forecast horizon. "
                  "Immediate management review and remediation recommended.",
    }
    msg = interpretations.get(risk_level, "")
    st.markdown(
        f"<div class='card card-accent' style='padding:14px 20px;margin-bottom:20px;'>"
        f"<p style='color:#cbd5e1;font-size:0.95rem;margin:0;line-height:1.65'>{msg}</p></div>",
        unsafe_allow_html=True,
    )

    # ── Sample paths chart ─────────────────────────────────────────────────────
    sample_paths: pd.DataFrame = result["sample_paths"]
    if not sample_paths.empty:
        st.divider()
        _section("Sample Simulation Paths — 20 of 1,000")
        st.caption(
            "Each line represents one simulated 12-month cumulative cash balance. "
            "Paths that fall below zero indicate potential insolvency."
        )
        chart_df = sample_paths.T
        chart_df.index.name = "Month"
        st.line_chart(chart_df, use_container_width=True, height=360)

    # ── Final balance distribution ─────────────────────────────────────────────
    final_balances = result["final_balances"]
    if len(final_balances) > 0:
        st.divider()
        _section("Final Balance Distribution — all simulations")
        st.caption(
            "Distribution of ending cash balances at month 12 across all simulations. "
            "Bars to the left of zero represent failed (insolvent) scenarios."
        )

        counts, bin_edges = np.histogram(final_balances, bins=40)
        hist_df = pd.DataFrame({
            "Balance":   bin_edges[:-1].round(0),
            "Frequency": counts,
        }).set_index("Balance")
        st.bar_chart(hist_df, color="#8b5cf6", use_container_width=True, height=280)

        # Survival stats summary
        survived_pct = float((final_balances > 0).mean() * 100)
        median_bal   = float(np.median(final_balances))
        p10_bal      = float(np.percentile(final_balances, 10))

        st.divider()
        _section("Distribution Statistics")
        s1, s2, s3 = st.columns(3)
        s1.metric("Survival Rate",       f"{survived_pct:.1f}%")
        s2.metric("Median Final Balance", f"$ {median_bal:,.0f}")
        s3.metric("10th Percentile",      f"$ {p10_bal:,.0f}")

    # ── Methodology note ───────────────────────────────────────────────────────
    st.divider()
    st.markdown(f"""
    <div class="card" style="padding:14px 20px;">
        <h3 style="font-size:0.88rem !important;border-bottom:none !important;
                   padding-bottom:0 !important;margin-bottom:8px !important;">
            📐 Methodology
        </h3>
        <p style="font-size:0.83rem;line-height:1.7;">
            Income and expense distributions are estimated from transaction data statistics
            (mean ± standard deviation). Each simulation draws monthly income and expense
            from independent Gaussian distributions, clips negatives to zero, and tracks
            the cumulative running balance.<br><br>
            <strong style="color:#e5e7eb">Audit stress signal:</strong>
            The anomaly rate from your dataset
            (<code style="color:#c4b5fd">{anomaly_rate*100:.1f}%</code> of transactions flagged)
            is applied as an expense multiplier
            (<code style="color:#c4b5fd">expense × {expense_mult:.2f}</code>),
            stressing projected cash outflows to reflect elevated fraud or control-failure risk.<br><br>
            <strong style="color:#e5e7eb">Going-concern survival definition:</strong>
            A simulation is deemed to <em>survive</em> if its cumulative cash balance
            at month {n_months} is above zero — i.e. the entity maintained positive cash
            throughout the entire forecast horizon.
            Survival probability = surviving simulations ÷ {n_ran:,} total simulations × 100.
        </p>
    </div>
    """, unsafe_allow_html=True)
