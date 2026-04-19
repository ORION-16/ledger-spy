"""
LedgerSpy – Data Integrity Checker
Validates data quality before ML analysis and computes a readiness score.
"""

import pandas as pd


# ── Column type expectations ──────────────────────────────────────────────────
NUMERIC_COLS = ["amount", "velocity_score", "vendor_location_risk"]
DATE_COLS = ["timestamp", "invoice_date", "due_date"]


# ── 1. Missing values ─────────────────────────────────────────────────────────
def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count missing values per column.

    Returns:
        DataFrame with columns: column, missing_count, missing_pct
    """
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)

    result = pd.DataFrame({
        "column": missing_count.index,
        "missing_count": missing_count.values,
        "missing_pct": missing_pct.values,
    })
    return result[result["missing_count"] > 0].reset_index(drop=True)


# ── 2. Duplicate rows ─────────────────────────────────────────────────────────
def check_duplicates(df: pd.DataFrame) -> dict:
    """
    Count fully duplicate rows.

    Returns:
        {"duplicate_count": int, "duplicate_pct": float}
    """
    dup_count = int(df.duplicated().sum())
    return {
        "duplicate_count": dup_count,
        "duplicate_pct": round(dup_count / len(df) * 100, 2) if len(df) else 0.0,
    }


# ── 3. Data-type issues ───────────────────────────────────────────────────────
def validate_data_types(df: pd.DataFrame) -> dict:
    """
    Check numeric columns for non-numeric values and date columns for
    unparseable values.

    Returns:
        {
            "numeric_issues": {col: count, ...},
            "date_issues":    {col: count, ...},
        }
    """
    numeric_issues = {}
    for col in NUMERIC_COLS:
        if col not in df.columns:
            continue
        coerced = pd.to_numeric(df[col], errors="coerce")
        n_bad = int(coerced.isna().sum() - df[col].isna().sum())
        if n_bad > 0:
            numeric_issues[col] = n_bad

    date_issues = {}
    for col in DATE_COLS:
        if col not in df.columns:
            continue
        coerced = pd.to_datetime(df[col], errors="coerce")
        n_bad = int(coerced.isna().sum() - df[col].isna().sum())
        if n_bad > 0:
            date_issues[col] = n_bad

    return {"numeric_issues": numeric_issues, "date_issues": date_issues}


# ── 4. Invalid values ─────────────────────────────────────────────────────────
def _check_invalid_values(df: pd.DataFrame) -> dict:
    """
    Flag domain-specific invalid values:
      - amount           : <= 0
      - velocity_score   : outside [0, 100]  (assumed 0–100 scale)
      - vendor_location_risk: outside [0, 1] (assumed 0–1 scale)

    Returns:
        {"invalid_<col>": count, ...}
    """
    result = {}

    if "amount" in df.columns:
        numeric_amount = pd.to_numeric(df["amount"], errors="coerce")
        result["invalid_amount"] = int((numeric_amount <= 0).sum())

    if "velocity_score" in df.columns:
        vs = pd.to_numeric(df["velocity_score"], errors="coerce")
        result["invalid_velocity_score"] = int(((vs < 0) | (vs > 100)).sum())

    if "vendor_location_risk" in df.columns:
        vr = pd.to_numeric(df["vendor_location_risk"], errors="coerce")
        result["invalid_vendor_location_risk"] = int(((vr < 0) | (vr > 1)).sum())

    return result


# ── 5. Readiness score ────────────────────────────────────────────────────────
def compute_readiness_score(df: pd.DataFrame) -> float:
    """
    Readiness Score = 100 − (pct_missing + pct_duplicates + pct_invalid_rows)
    Clamped to [0, 100].

    Args:
        df: Transactions DataFrame.

    Returns:
        Float readiness score 0–100.
    """
    n = len(df)
    if n == 0:
        return 0.0

    # % missing (average across all cells)
    pct_missing = df.isnull().sum().sum() / (n * len(df.columns)) * 100

    # % duplicate rows
    pct_dup = df.duplicated().sum() / n * 100

    # % invalid rows (rows with at least one invalid domain value)
    invalid_masks = []
    if "amount" in df.columns:
        amt = pd.to_numeric(df["amount"], errors="coerce")
        invalid_masks.append(amt <= 0)
    if "velocity_score" in df.columns:
        vs = pd.to_numeric(df["velocity_score"], errors="coerce")
        invalid_masks.append((vs < 0) | (vs > 100))
    if "vendor_location_risk" in df.columns:
        vr = pd.to_numeric(df["vendor_location_risk"], errors="coerce")
        invalid_masks.append((vr < 0) | (vr > 1))

    if invalid_masks:
        combined_invalid = pd.concat(invalid_masks, axis=1).any(axis=1)
        pct_invalid = combined_invalid.sum() / n * 100
    else:
        pct_invalid = 0.0

    score = 100 - (pct_missing + pct_dup + pct_invalid)
    return round(max(0.0, min(100.0, score)), 2)


# ── 6. Full report ────────────────────────────────────────────────────────────
def get_integrity_report(df: pd.DataFrame) -> dict:
    """
    Run all checks and return a single consolidated report dict.

    Returns:
        {
            "readiness_score":   float,
            "missing_summary":   pd.DataFrame,
            "duplicate_count":   int,
            "duplicate_pct":     float,
            "type_issues":       dict,
            "invalid_counts":    dict,
            "total_rows":        int,
        }
    """
    missing_summary = check_missing_values(df)
    dup_info = check_duplicates(df)
    type_issues = validate_data_types(df)
    invalid_counts = _check_invalid_values(df)
    readiness_score = compute_readiness_score(df)

    return {
        "readiness_score": readiness_score,
        "missing_summary": missing_summary,
        "duplicate_count": dup_info["duplicate_count"],
        "duplicate_pct": dup_info["duplicate_pct"],
        "type_issues": type_issues,
        "invalid_counts": invalid_counts,
        "total_rows": len(df),
    }

   