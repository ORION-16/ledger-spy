"""
modules/benchmark.py
Privacy-Preserving Industry Benchmarking
Compares company anomaly rate to an industry baseline using differential privacy noise.
"""

import numpy as np
import pandas as pd


# Industry baseline anomaly rate (public domain assumption ~8%)
INDUSTRY_BASELINE_PCT: float = 8.0

# Gaussian noise scale for differential privacy (sigma = 0.5%)
_DP_NOISE_SIGMA: float = 0.5


def benchmark_anomaly_rate(df: pd.DataFrame, dp_noise: bool = True) -> dict:
    """
    Compare the company's anomaly rate against the industry baseline.

    Expects df to have a column named 'risk' (numeric, 0–1 probability) OR
    a boolean/int column 'is_anomaly'. Falls back gracefully if neither exists.

    Privacy: adds small Gaussian noise (σ=0.5pp) to the reported company rate
    so the exact figure is never disclosed — only the noisy estimate is shown.

    Returns
    -------
    dict with keys:
        company_rate_raw    : float   (true rate, %)
        company_rate_noisy  : float   (differentially private rate, %)
        industry_baseline   : float   (%)
        delta_pp            : float   (noisy company − baseline, pp)
        comparison          : str     ("Better than industry" | "Worse than industry" | "On par")
        comparison_color    : str     (hex)
        risk_column_used    : str     (which column was used)
        n_transactions      : int
        n_flagged           : int
    """

    if df is None or df.empty:
        return _empty_result()

    # ── Detect which column to use ────────────────────────────────────────────
    if "risk" in df.columns:
        col = "risk"
        rates = pd.to_numeric(df[col], errors="coerce").dropna()
        # If values are 0–1 probabilities, convert to binary using 0.5 threshold
        if rates.max() <= 1.0:
            flagged = (rates >= 0.5).sum()
        else:
            # Already a 0/1 integer column
            flagged = (rates > 0).sum()
    elif "is_anomaly" in df.columns:
        col = "is_anomaly"
        rates = pd.to_numeric(df[col], errors="coerce").dropna()
        flagged = rates.sum()
    elif "hybrid_risk_score" in df.columns:
        col = "hybrid_risk_score"
        rates = pd.to_numeric(df[col], errors="coerce").dropna()
        flagged = (rates >= 0.5).sum()
    else:
        return _empty_result(reason="No risk/is_anomaly column found in dataframe.")

    n_total       = len(df)
    n_flagged     = int(flagged)
    company_rate  = (n_flagged / n_total * 100) if n_total > 0 else 0.0

    # ── Differential privacy noise (Step 5) ──────────────────────────────────
    # Gaussian mechanism: add N(0, sigma) noise to company_rate before disclosure.
    # Clamped to [0, 100] so the noisy figure is always a valid percentage.
    np.random.seed(None)   # fresh seed each call for genuine randomness
    noise       = np.random.normal(0, _DP_NOISE_SIGMA) if dp_noise else 0.0
    noisy_rate  = float(np.clip(company_rate + noise, 0.0, 100.0))
    noisy_rate  = round(noisy_rate, 2)

    delta_pp    = round(noisy_rate - INDUSTRY_BASELINE_PCT, 2)

    # ── Relative ratio vs industry baseline (Step 4) ──────────────────────────
    relative_ratio = round(noisy_rate / INDUSTRY_BASELINE_PCT, 2) if INDUSTRY_BASELINE_PCT > 0 else 0.0

    # ── Comparison label ──────────────────────────────────────────────────────
    tolerance = 1.0   # within ±1pp = "on par"
    if delta_pp < -tolerance:
        comparison       = "✅  Better than industry"
        comparison_color = "#4ade80"
    elif delta_pp > tolerance:
        comparison       = "⚠️  Worse than industry"
        comparison_color = "#f87171"
    else:
        comparison       = "➡️  On par with industry"
        comparison_color = "#fcd34d"

    return {
        "company_rate_raw":   round(company_rate, 2),
        "company_rate_noisy": noisy_rate,
        "industry_baseline":  INDUSTRY_BASELINE_PCT,
        "delta_pp":           delta_pp,
        "relative_ratio":     relative_ratio,   # Step 4: X times vs baseline
        "comparison":         comparison,
        "comparison_color":   comparison_color,
        "risk_column_used":   col,
        "n_transactions":     n_total,
        "n_flagged":          n_flagged,
    }


def _empty_result(reason: str = "No data available.") -> dict:
    return {
        "company_rate_raw":   None,
        "company_rate_noisy": None,
        "industry_baseline":  INDUSTRY_BASELINE_PCT,
        "delta_pp":           None,
        "relative_ratio":     None,
        "comparison":         reason,
        "comparison_color":   "#6b7280",
        "risk_column_used":   "N/A",
        "n_transactions":     0,
        "n_flagged":          0,
    }