"""
LedgerSpy - Fuzzy Entity Reconciliation
Detects vendors with similar names (possible duplicates or fraud).
"""

from itertools import combinations
import pandas as pd
from rapidfuzz import fuzz


def _find_similar_vendors(df: pd.DataFrame, threshold: int = 85) -> pd.DataFrame:
    """
    Compare all unique vendor_name values using fuzzy string matching.

    Args:
        df: DataFrame with at least a 'vendor_name' column.
        threshold: Minimum similarity score (0–100) to include a pair.

    Returns:
        DataFrame with columns: vendor_1, vendor_2, similarity
    """
    unique_vendors = df["vendor_name"].dropna().unique().tolist()
    records = []

    for v1, v2 in combinations(unique_vendors, 2):
        score = fuzz.token_sort_ratio(v1, v2)
        if score >= threshold:
            records.append({"vendor_1": v1, "vendor_2": v2, "similarity": score})

    if not records:
        return pd.DataFrame(columns=["vendor_1", "vendor_2", "similarity"])

    return pd.DataFrame(records).sort_values("similarity", ascending=False).reset_index(drop=True)


def enrich_with_context(df: pd.DataFrame, matches_df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich matched vendor pairs with transaction context.

    For each pair adds:
      - shared_approver: comma-separated intersection of approvers
      - shared_department: comma-separated intersection of departments
      - txn_count: total combined transactions
      - avg_amount: average amount across both vendors

    Args:
        df: Full transactions DataFrame.
        matches_df: Output of find_similar_vendors().

    Returns:
        Enriched DataFrame.
    """
    if matches_df.empty:
        return matches_df.assign(
            shared_approver="",
            shared_department="",
            txn_count=0,
            avg_amount=0.0,
        )

    enriched_rows = []

    for _, row in matches_df.iterrows():
        v1, v2 = row["vendor_1"], row["vendor_2"]

        txns_v1 = df[df["vendor_name"] == v1]
        txns_v2 = df[df["vendor_name"] == v2]

        approvers_v1 = set(txns_v1["approver"].dropna().unique())
        approvers_v2 = set(txns_v2["approver"].dropna().unique())
        shared_approvers = approvers_v1 & approvers_v2

        depts_v1 = set(txns_v1["department"].dropna().unique())
        depts_v2 = set(txns_v2["department"].dropna().unique())
        shared_depts = depts_v1 & depts_v2

        combined_txns = pd.concat([txns_v1, txns_v2])
        txn_count = len(combined_txns)
        avg_amount = combined_txns["amount"].mean() if txn_count > 0 else 0.0

        enriched_rows.append(
            {
                **row.to_dict(),
                "shared_approver": ", ".join(sorted(shared_approvers)) if shared_approvers else "",
                "shared_department": ", ".join(sorted(shared_depts)) if shared_depts else "",
                "txn_count": txn_count,
                "avg_amount": round(avg_amount, 2),
            }
        )

    return pd.DataFrame(enriched_rows).reset_index(drop=True)


def compute_risk_scores(df: pd.DataFrame, threshold: int = 85) -> pd.DataFrame:
    """
    Full pipeline: find similar vendors, enrich with context, assign risk level.

    Risk logic:
      - HIGH   : similarity > 90 AND shared_approver is non-empty
      - MEDIUM : similarity > 85
      - LOW    : otherwise

    Args:
        df: Full transactions DataFrame.
        threshold: Minimum similarity score.

    Returns:
        DataFrame with columns:
        vendor_1 | vendor_2 | similarity | shared_approver |
        shared_department | txn_count | avg_amount | risk
    """
    matches_df = _find_similar_vendors(df, threshold=threshold)

    if matches_df.empty:
        return pd.DataFrame(
            columns=[
                "vendor_1", "vendor_2", "similarity",
                "shared_approver", "shared_department",
                "txn_count", "avg_amount", "risk",
            ]
        )

    enriched_df = enrich_with_context(df, matches_df)

    def _assign_risk(row):
        if row["similarity"] > 90 and row["shared_approver"]:
            return "HIGH"
        if row["similarity"] > 85:
            return "MEDIUM"
        return "LOW"

    enriched_df["risk"] = enriched_df.apply(_assign_risk, axis=1)

    # Reorder columns to match spec
    cols = [
        "vendor_1", "vendor_2", "similarity",
        "shared_approver", "shared_department",
        "txn_count", "avg_amount", "risk",
    ]
    return enriched_df[cols].reset_index(drop=True)


def find_similar_vendors(df):
    try:
        data = df.copy()

        # Handle alias columns
        aliases = {"vendor_name": ["vendor", "merchant", "payee", "beneficiary", "supplier", "merchant_name"],
                   "approver": ["authorized_by", "manager", "employee"],
                   "department": ["dept", "business_unit", "cost_center"],
                   "amount": ["txn_amount", "transaction_amount", "value"]}

        # Standardize columns to expected names if missing
        for standard_name, possible_aliases in aliases.items():
            if standard_name not in data.columns:
                for alias in possible_aliases:
                    if alias in data.columns:
                        data[standard_name] = data[alias]
                        break
            
            # If still missing, fill
            if standard_name not in data.columns:
                data[standard_name] = "unknown"
                if standard_name == "amount":
                    data[standard_name] = 0.0

        # Compute matches
        result = compute_risk_scores(data)
        
        items = result.to_dict(orient="records")
        
        # If no fuzzy matches exist, return a dummy row so 'vendors' isn't evaluated as falsy
        # which triggers the "No fuzzy matching data available." info blocker in the UI
        if len(items) == 0:
            return [{"vendor_1": "No matches found", "vendor_2": "", "similarity": 0, "shared_approver": "", "shared_department": "", "txn_count": 0, "avg_amount": 0.0, "risk": "LOW"}]
            
        return items

    except Exception as e:
        print("FUZZY ERROR:", e)
        return [{"vendor_1": "Error Processing Data", "vendor_2": str(e), "similarity": 0, "shared_approver": "", "shared_department": "", "txn_count": 0, "avg_amount": 0.0, "risk": "LOW"}]
