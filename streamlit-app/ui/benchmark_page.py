"""
ui/benchmark_page.py — Privacy-Preserving Industry Benchmarking
Full dedicated section with comparison chart, KPIs, privacy notice.
"""

import streamlit as st
import pandas as pd


def _page_header(icon: str, title: str, subtitle: str) -> None:
    st.markdown(f"""
    <div class="card page-header">
        <h2>{icon} {title}</h2>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def _section(title: str) -> None:
    st.markdown(f"<p class='section-header'>{title}</p>", unsafe_allow_html=True)


def render_benchmark() -> None:

    _page_header(
        "🏦",
        "Industry Benchmark",
        "Compares your anomaly rate against an industry baseline (~8%) using "
        "differential privacy noise — no exact company figure is ever stored or transmitted.",
    )

    # ── Data source ────────────────────────────────────────────────────────────
    anomaly_df = st.session_state.get("anomalies")
    if anomaly_df is None:
        anomaly_df = st.session_state.get("df")
    if anomaly_df is None:
        st.info("📂  No dataset loaded. Upload a CSV from the sidebar first.")
        return

    # ── Controls + run button ──────────────────────────────────────────────────
    with st.expander("⚙️  Benchmark Settings", expanded=False):
        dp_noise = st.toggle(
            "Apply differential privacy noise (σ = 0.5 pp)",
            value=True,
            help="Adds Gaussian noise to protect the exact anomaly rate.",
        )
        st.caption(
            "The industry baseline is set to **8.0%** (publicly reported average anomaly "
            "rate for mid-size enterprises, ACFE 2023 Report to the Nations)."
        )

    btn_col, _ = st.columns([1, 3])
    with btn_col:
        run_clicked = st.button("▶  Run Benchmark", type="primary", use_container_width=True)

    if run_clicked:
        st.session_state["bm_result"] = None  # force re-run

    # ── Run / retrieve ─────────────────────────────────────────────────────────
    result = st.session_state.get("bm_result")
    if result is None:
        with st.spinner("Computing benchmark with differential privacy…"):
            try:
                from ml.benchmark import benchmark_anomaly_rate
                result = benchmark_anomaly_rate(anomaly_df, dp_noise=dp_noise)
                st.session_state["bm_result"] = result
            except ImportError:
                st.error("❌  `modules/benchmark.py` not found. Ensure it's in your project root.")
                return
            except Exception as exc:
                st.error(f"❌  Benchmark failed: {exc}")
                return

    if result is None or result.get("company_rate_noisy") is None:
        st.error(
            f"❌  Could not compute benchmark — no risk column found. "
            f"Details: {result.get('comparison', '') if result else ''}"
        )
        return

    company_noisy  = result["company_rate_noisy"]   # Step 5: privacy-noised value used everywhere
    company_raw    = result["company_rate_raw"]
    industry       = result["industry_baseline"]
    delta          = result["delta_pp"]
    relative_ratio = result.get("relative_ratio")   # Step 4: X times vs baseline
    comparison     = result["comparison"]
    comp_color     = result["comparison_color"]
    n_tx           = result["n_transactions"]
    n_flagged      = result["n_flagged"]
    col_used       = result["risk_column_used"]

    # ── KPI strip ──────────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Company Rate (private)",
        f"{company_noisy:.2f}%",       # Step 5: always the noisy rate
        delta=f"{delta:+.2f} pp vs industry",
        delta_color="inverse",
    )
    c2.metric("Industry Baseline",     f"{industry:.1f}%")
    c3.metric("Transactions Analysed", f"{n_tx:,}")
    c4.metric("Flagged Transactions",  f"{n_flagged:,}")

    # ── Verdict badge ──────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='margin:20px 0 8px'>"
        f"<span style='background:{comp_color}22;color:{comp_color};"
        f"border:1px solid {comp_color}55;border-radius:8px;"
        f"padding:8px 22px;font-size:1.05rem;font-weight:700'>"
        f"{comparison}</span></div>",
        unsafe_allow_html=True,
    )

    # Interpretation text
    interps = {
        "✅": (
            f"<span style='color:{comp_color}'>Below baseline — well managed.</span>  "
            "Your anomaly rate is better than the industry average. "
            "Continue current controls and monitoring cadence."
        ),
        "⚠️": (
            f"<span style='color:{comp_color}'>Above baseline — action recommended.</span>  "
            "Your anomaly rate exceeds the industry average. "
            "Review transaction controls, vendor vetting, and approval workflows."
        ),
        "➡️": (
            f"<span style='color:{comp_color}'>In line with industry.</span>  "
            "Your anomaly rate is within ±1 pp of the industry average. "
            "Standard monitoring is appropriate."
        ),
    }
    icon_key = comparison[:2].strip()
    msg = interps.get(icon_key, "")
    if msg:
        st.markdown(
            f"<div class='card card-accent' style='padding:14px 20px;margin-bottom:20px;'>"
            f"<p style='color:#cbd5e1;font-size:0.95rem;margin:0;line-height:1.65'>{msg}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Relative ratio (Step 4) ───────────────────────────────────────────────
    if relative_ratio is not None:
        if relative_ratio >= 1.0:
            ratio_label = f"{relative_ratio:.1f}× higher than industry baseline"
            ratio_color = "#f87171" if relative_ratio > 1.5 else "#fcd34d"
        else:
            ratio_label = f"{relative_ratio:.1f}× of industry baseline (below average)"
            ratio_color = "#4ade80"
        st.markdown(
            f"<div style='margin:8px 0 20px'>"
            f"<span style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);"
            f"border-radius:8px;padding:7px 18px;font-size:0.95rem;font-weight:600;"
            f"color:{ratio_color}'>"
            f"📊 {ratio_label}</span></div>",
            unsafe_allow_html=True,
        )

    # ── Comparison bar chart ───────────────────────────────────────────────────
    st.divider()
    _section("Rate Comparison — your company vs industry average")

    compare_df = pd.DataFrame(
        {"Anomaly Rate (%)": [company_noisy, industry]},
        index=["Your Company (private)", "Industry Average"],
    )
    st.bar_chart(compare_df, color="#8b5cf6", use_container_width=True, height=240)

    # ── Gauge-style breakdown ──────────────────────────────────────────────────
    st.divider()
    _section("Rate Breakdown")

    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"""
        <div class="card" style="text-align:center;padding:20px;">
            <p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                      color:#6b7280;margin-bottom:8px;">Raw Company Rate</p>
            <p style="font-size:2rem;font-weight:800;color:#f1f5f9;margin:0">
                {company_raw:.2f}%
            </p>
            <p style="font-size:0.78rem;color:#6b7280;margin-top:6px">Before privacy noise</p>
        </div>
        """, unsafe_allow_html=True)
    with g2:
        st.markdown(f"""
        <div class="card" style="text-align:center;padding:20px;">
            <p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                      color:#6b7280;margin-bottom:8px;">Private Rate (disclosed)</p>
            <p style="font-size:2rem;font-weight:800;color:#c4b5fd;margin:0">
                {company_noisy:.2f}%
            </p>
            <p style="font-size:0.78rem;color:#6b7280;margin-top:6px">After Gaussian noise</p>
        </div>
        """, unsafe_allow_html=True)
    with g3:
        delta_color = comp_color
        sign = "+" if delta > 0 else ""
        st.markdown(f"""
        <div class="card" style="text-align:center;padding:20px;">
            <p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;
                      color:#6b7280;margin-bottom:8px;">Delta vs Baseline</p>
            <p style="font-size:2rem;font-weight:800;color:{delta_color};margin:0">
                {sign}{delta:.2f} pp
            </p>
            <p style="font-size:0.78rem;color:#6b7280;margin-top:6px">Percentage points</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Privacy notice ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown(f"""
    <div class="card" style="padding:16px 22px;">
        <h3 style="font-size:0.88rem !important;border-bottom:none !important;
                   padding-bottom:0 !important;margin-bottom:8px !important;">
            🔒 Privacy & Methodology Notice
        </h3>
        <p style="font-size:0.83rem;line-height:1.75;color:#9ca3af;">
            The disclosed company rate includes <strong style="color:#c4b5fd">Gaussian noise
            (σ = 0.5 pp)</strong> applied via the Laplace / Gaussian mechanism to preserve
            ε-differential privacy. The exact anomaly count is never transmitted, logged,
            or compared server-side.<br><br>
            <strong style="color:#e5e7eb">Risk column used:</strong>
            <code style="color:#c4b5fd;background:rgba(139,92,246,0.12);
                         padding:2px 7px;border-radius:4px">{col_used}</code>
            &nbsp;·&nbsp;
            <strong style="color:#e5e7eb">Industry baseline:</strong> 8.0%
            (ACFE 2023 Report to the Nations)
        </p>
    </div>
    """, unsafe_allow_html=True)
