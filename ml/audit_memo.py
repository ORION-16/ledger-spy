def generate_audit_memo(df, risk_scores, readiness):
    import datetime
    try:
        total = risk_scores.get("total", len(df))
        anomalies = risk_scores.get("anomaly_count", 0)
        risk_level = risk_scores.get("overall_risk", "Medium")

        null_pct = readiness.get("null_pct", 0)
        dup_pct = readiness.get("dup_pct", 0)
        col_count = readiness.get("col_count", len(df.columns))

        # Dynamically extract basic statistics from the DataFrame
        amount_col = next((col for col in df.columns if "amount" in col.lower()), None)
        total_val = float(df[amount_col].sum()) if amount_col else 0.0
        avg_val = float(df[amount_col].mean()) if amount_col else 0.0
        max_val = float(df[amount_col].max()) if amount_col and not df.empty else 0.0
        
        vendor_col = next((col for col in df.columns if "vendor" in col.lower()), None)
        unique_vendors = df[vendor_col].nunique() if vendor_col else "Unknown"

        # Benford / Fraud indicators (rough estimations if exact not present)
        is_fraud_col = next((col for col in df.columns if "fraud" in col.lower() or "suspicious" in col.lower()), None)
        fraud_flags = int(df[is_fraud_col].sum()) if is_fraud_col else 0

        # High-risk threshold (configurable)
        high_value_trans = int((df[amount_col] > (avg_val * 3)).sum()) if amount_col else 0

        anomaly_pct = (anomalies / max(total, 1)) * 100

        memo = f"""
================================================================================
                       LEDGERSPY FORENSIC AUDIT MEMO
================================================================================
Generated On: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Overall Risk Assessment: {risk_level.upper()}
--------------------------------------------------------------------------------

1. EXECUTIVE SUMMARY
--------------------
An automated forensic analysis and integrity check was performed on the provided 
ledger data. The platform ingested {total:,} transactions across {col_count} data dimensions. 
The dataset presents a {risk_level.upper()} level of audit risk, primarily evaluated 
through statistical anomalies and structural inconsistencies.

2. DATA AND FINANCIAL PROFILE
-----------------------------
Timeframe:             {date_range}
Total Transactions:    {total:,}
Unique Vendors:        {unique_vendors}
Total Value Processed: ${total_val:,.2f}
Average Transaction:   ${avg_val:,.2f}
Maximum Transaction:   ${max_val:,.2f}
High-Value Anomalous:  {high_value_trans:,} transactions exceed 3x the average.

3. DATA INTEGRITY & QUALITY
---------------------------
Missing Data (Nulls):  {null_pct:.2f}%
Duplicate Records:     {dup_pct:.2f}%

Quality Conclusion: 
{"[PASS] Data integrity appears robust with minimal gaps, supporting reliable analytics." if null_pct < 5 else "[WARNING] Significant data gaps were observed >5%, which may mask underlying risks and limit analytical precision."}
{"[PASS] Duplicate record ratio is within acceptable limits." if dup_pct < 2 else "[WARNING] High duplicate ratio detected (>2%). A detailed review for accidental dual-payments is advised."}

4. FORENSIC FINDINGS
--------------------
FINDING 4.1: Statistical Anomalies
A total of {anomalies:,} transactions ({anomaly_pct:.2f}% of volume) were flagged by 
the machine learning algorithms as anomalous. These represent statistical outliers 
in value, frequency, or categorical distribution.

FINDING 4.2: High-Value Expenditure Checks
There are {high_value_trans:,} transactions recorded that are over 300% of the dataset's 
average transaction volume. These outsized transactions heavily skew the financial 
statements and require individual substantive vouching.

FINDING 4.3: Pre-Flagged Risk Events
The ledger contains {fraud_flags:,} events that align with hard-coded suspicious flags 
or known fraudulent markers within the dataset mapping.

FINDING 4.4: Relational Risk 
Entity mapping evaluated the dataset for potential conflicts. Vendor and approver 
concentrations should be cross-referenced with internal approval limits, 
especially targeting the maximum recorded transaction of ${max_val:,.2f}.

5. AUDIT RECOMMENDATIONS
------------------------
- Vouching & Sampling: Extrapolate a substantive sample from the {anomalies:,} flagged 
  anomalies for vouching against original invoices and contracts.
- High-Risk Validation: Retrieve direct bank statements corresponding to the 
  top 10 largest disbursements out of the {high_value_trans} high-value transactions.
- Master File Scrub: Conduct a vendor master file review focusing on the {unique_vendors} 
  identified vendors to detect overlapping corporate addresses or fuzzy duplicates.
- Approval Verification: Verify explicit management approval for individual 
  transactions exceeding standard organizational thresholds.

6. CONCLUSION
-------------
Based on the LedgerSpy analysis, it is recommended to adjust substantive testing 
procedures to account for a {risk_level.upper()} risk environment. Further investigation 
of the flagged anomalies is required before concluding on the material accuracy 
of the financial statements.
================================================================================
"""
        return memo.strip()

    except Exception as e:
        print("AUDIT MEMO ERROR:", e)
        return "Audit memo could not be generated."
