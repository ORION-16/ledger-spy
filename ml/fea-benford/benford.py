"""
LedgerSpy – Benford's Law / Digital Frequency Profiling
Detects fabricated transaction amounts by comparing first-digit distributions.
"""

import math
import pandas as pd


# ── Benford expected probabilities for digits 1–9 ────────────────────────────
BENFORD_EXPECTED = {
    d: math.log10(1 + 1 / d) for d in range(1, 10)
}


def compute_benford_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the first digit of each `amount` and compute actual vs expected
    Benford frequencies.

    Args:
        df: Transactions DataFrame with an `amount` column.

    Returns:
        DataFrame with columns: digit, actual_freq, expected_freq
    """
    amounts = df["amount"].dropna()
    # Keep only positive amounts (negative / zero have no meaningful first digit)
    amounts = amounts[amounts > 0]

    if amounts.empty:
        rows = [
            {"digit": d, "actual_freq": 0.0, "expected_freq": round(BENFORD_EXPECTED[d], 6)}
            for d in range(1, 10)
        ]
        return pd.DataFrame(rows)

    first_digits = amounts.astype(str).str.lstrip("0").str[0]
    first_digits = first_digits[first_digits.str.isdigit()].astype(int)
    first_digits = first_digits[first_digits.between(1, 9)]

    total = len(first_digits)
    actual_counts = first_digits.value_counts().reindex(range(1, 10), fill_value=0)
    actual_freq = actual_counts / total

    rows = [
        {
            "digit": d,
            "actual_freq": round(float(actual_freq[d]), 6),
            "expected_freq": round(BENFORD_EXPECTED[d], 6),
        }
        for d in range(1, 10)
    ]
    return pd.DataFrame(rows)


def calculate_deviation(df_benford: pd.DataFrame) -> pd.DataFrame:
    """
    Add a `deviation` column (absolute difference) to a Benford distribution
    DataFrame.

    Args:
        df_benford: Output of compute_benford_distribution().

    Returns:
        Same DataFrame with an added `deviation` column.
    """
    result = df_benford.copy()
    result["deviation"] = (result["actual_freq"] - result["expected_freq"]).abs().round(6)
    return result


def get_benford_summary(df: pd.DataFrame) -> dict:
    """
    Full pipeline: compute distribution, calculate deviations, and return a
    summary dict.

    The overall_deviation_score is the Mean Absolute Deviation (MAD) across
    all 9 digits, scaled to 0–100 (higher = more suspicious).

    Args:
        df: Transactions DataFrame.

    Returns:
        {
            "benford_df": pd.DataFrame   # digit | actual_freq | expected_freq | deviation
            "overall_deviation_score": float  # 0–100
        }
    """
    benford_df = compute_benford_distribution(df)
    benford_df = calculate_deviation(benford_df)

    # MAD: maximum possible MAD ≈ 1.0 (all mass on one digit), scale to 100
    mad = float(benford_df["deviation"].mean())
    overall_deviation_score = round(min(mad * 100 / 0.3, 100), 2)  # 0.3 ≈ practical max

    return {
        "benford_df": benford_df,
        "overall_deviation_score": overall_deviation_score,
    }
def benford_analysis(df):
    try:
        result = get_benford_summary(df)

        # return ONLY what UI expects
        benford_df = result["benford_df"]

        # convert to simple dict: {digit: actual_freq}
        return {
            int(row["digit"]): float(row["actual_freq"]) * 100
            for _, row in benford_df.iterrows()
        }

    except Exception as e:
        print("BENFORD ERROR:", e)
        return {i: 0 for i in range(1, 10)}