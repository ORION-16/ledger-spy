from ui.styles import apply_global_styles
import streamlit as st
import pandas as pd


def render_reconciliation():
    apply_global_styles()
    
    st.markdown("""
    <div class="card" style="padding: 16px 24px; margin-bottom: 24px;">
        <h2 style="margin: 0; display: flex; align-items: center; gap: 10px;">
            🏦 Bank Reconciliation
        </h2>
        <p style="margin-top: 4px; color: #9ca3af;">Match ledger transactions with bank records and identify mismatches.</p>
    </div>
    """, unsafe_allow_html=True)

    data = st.session_state.get("reconciliation")

    # ── Bank CSV uploader ────────────────────────────────────────────────────
    # reconcile() needs TWO dataframes: ledger (already uploaded) + bank CSV.
    # We let the user upload the bank statement right here in this view.
    if "df" not in st.session_state:
        st.info("No ledger data available. Please upload a dataset to process.")
        return

    st.subheader("📂 Upload Bank Statement")
    bank_file = st.file_uploader(
        "Upload your Bank CSV (must contain: invoice_id, bank_txn_id, amount)",
        type=["csv"],
        key="bank_csv_uploader",
    )

    if bank_file is not None:
        try:
            bank_df = pd.read_csv(bank_file)
            # Ensure columns are perfectly normalized
            bank_df.columns = bank_df.columns.str.strip().str.lower().str.replace(' ', '_')

            # Smart aliasing for bank statement columns
            bank_alias_map = {
                'transaction_id': 'bank_txn_id',
                'txn_id': 'bank_txn_id',
                'id': 'bank_txn_id',
                'transaction_amount': 'amount',
                'value': 'amount'
            }
            bank_df.rename(columns=bank_alias_map, inplace=True)

            from ml.fea_reconcilation.recon import reconcile

            # Use a copy so we don't accidentally mutate the global df
            ledger_df = st.session_state["df"].copy()
            ledger_df.columns = ledger_df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            from ml.fea_reconcilation.recon import reconcile
            rec_output = reconcile(ledger_df, bank_df)

            if not hasattr(rec_output, "columns"):
                rec_output = pd.DataFrame(rec_output)

            st.session_state["reconciliation"] = rec_output
            st.session_state["reconciliation_simulated"] = False
            data = rec_output
        except Exception as e:
            st.error(f"Reconciliation failed: {e}", icon="🚨")
            return

    if data is None or not hasattr(data, "columns") or len(data) == 0:
        st.info(
            "Upload a bank statement above to run reconciliation.",
            icon="ℹ️",
        )
        return

    # Warning for simulation
    if st.session_state.get("reconciliation_simulated", False):
        st.warning("⚠️ No bank data detected. Showing simulated reconciliation results for demo.")

    # ── KPIs ─────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Summary")

    total = len(data)
    status_col_present = "status" in data.columns

    if status_col_present:
        matched   = int((data["status"] == "MATCHED").sum())
        missing   = int((data["status"] == "MISSING").sum())
        partial   = int((data["status"] == "PARTIAL").sum())
        unmatched = missing + partial
    else:
        matched = unmatched = missing = partial = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transactions", total)
    col2.metric("✅ Matched",         matched)
    col3.metric("❌ Missing",          missing)
    col4.metric("⚠️ Partial",          partial)

    st.divider()

    # ── Filter ───────────────────────────────────────────────────────────────
    st.subheader("🔍 Filter Results")

    filtered = data.copy()
    if status_col_present:
        filter_option = st.selectbox(
            "Show:",
            ["All", "Matched", "Missing", "Partial"],
            key="recon_filter",
        )
        status_map = {
            "Matched": "MATCHED",
            "Missing": "MISSING",
            "Partial": "PARTIAL",
        }
        if filter_option in status_map:
            filtered = data[data["status"] == status_map[filter_option]]

    # ── Results table ─────────────────────────────────────────────────────────
    st.subheader("📋 Results")
    MAX_ROWS = 500
    st.caption(f"Showing {min(len(filtered), MAX_ROWS)} of {len(filtered)} rows")

    def _color_status(val):
        colors = {
            "MATCHED": "background-color: #d4edda; color: #155724;",
            "MISSING": "background-color: #f8d7da; color: #721c24;",
            "PARTIAL": "background-color: #fff3cd; color: #856404;",
        }
        return colors.get(val, "")

    display_df = filtered.head(MAX_ROWS)

    if status_col_present:
        st.dataframe(
            display_df.style.map(_color_status, subset=["status"]),
            use_container_width=True,
        )
    else:
        st.dataframe(display_df, use_container_width=True)

    # ── Download ─────────────────────────────────────────────────────────────
    st.download_button(
        label="⬇️ Download Results as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="reconciliation_results.csv",
        mime="text/csv",
    )
