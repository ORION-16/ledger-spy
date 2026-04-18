"""
modules/monte_carlo.py
Monte Carlo Going Concern Stress Test
Simulates 12-month cash flow using transaction data statistics.
"""

import numpy as np
import pandas as pd


def monte_carlo_simulation(
    df: pd.DataFrame,
    n_simulations: int = 1000,
    n_months: int = 12,
    anomaly_rate: float = 0.0,
) -> dict:
    """
    Run Monte Carlo Going Concern cash flow simulation from transaction data.

    Expects a DataFrame with an 'amount' column (positive = income, negative = expense).
    If all values are positive, treats them as expenses and estimates income as a fixed multiple.

    Parameters
    ----------
    anomaly_rate : float
        Fraction of transactions flagged as anomalous (0–1). Used as an audit stress
        signal: expense_multiplier = 1 + anomaly_rate, inflating simulated expenses
        to reflect heightened operational / fraud risk.

    Returns
    -------
    dict with keys:
        survival_probability  : float  (0–100)
        risk_level            : str    ("Low" | "Medium" | "High")
        risk_color            : str    (hex colour for UI)
        sample_paths          : pd.DataFrame  (20 sample simulation paths, shape 20 × n_months)
        final_balances        : np.ndarray    (all final balances, length n_simulations)
        avg_monthly_income    : float
        avg_monthly_expense   : float  (after audit stress multiplier)
        avg_monthly_expense_base : float  (before multiplier, for display)
        expense_multiplier    : float
        n_simulations         : int
    """

    if df is None or df.empty or "amount" not in df.columns:
        return _empty_result()

    amounts = pd.to_numeric(df["amount"], errors="coerce").dropna()
    if amounts.empty:
        return _empty_result()

    # ── Separate income vs expense ───────────────────────────────────────────
    income_vals  = amounts[amounts > 0]
    expense_vals = amounts[amounts < 0].abs()

    # Fallback: if all positive treat every transaction as an expense
    # and estimate income as 1.05× mean expense (thin margin scenario)
    if income_vals.empty:
        avg_income  = float(expense_vals.mean()) * 1.05
        std_income  = float(expense_vals.std(ddof=1)) * 0.3 if len(expense_vals) > 1 else avg_income * 0.1
    else:
        avg_income  = float(income_vals.mean())
        std_income  = float(income_vals.std(ddof=1)) if len(income_vals) > 1 else avg_income * 0.1

    if expense_vals.empty:
        avg_expense = avg_income * 0.80
        std_expense = avg_expense * 0.1
    else:
        avg_expense = float(expense_vals.mean())
        std_expense = float(expense_vals.std(ddof=1)) if len(expense_vals) > 1 else avg_expense * 0.1

    # Clamp stds to avoid zero-division or degenerate simulations
    std_income  = max(std_income,  avg_income  * 0.05)
    std_expense = max(std_expense, avg_expense * 0.05)

    # ── Audit signal stress factor ────────────────────────────────────────────
    # Higher anomaly rates indicate elevated fraud / control-failure risk.
    # expense_multiplier = 1 + anomaly_rate so a 10% anomaly rate inflates
    # simulated monthly expenses by 10%, directly stressing cash flow.
    anomaly_rate        = max(0.0, min(1.0, float(anomaly_rate)))  # clamp [0,1]
    expense_multiplier  = 1.0 + anomaly_rate
    stressed_expense    = avg_expense * expense_multiplier
    stressed_std_exp    = std_expense * expense_multiplier   # scale std proportionally

    np.random.seed(42)

    # Shape: (n_simulations, n_months)
    monthly_income  = np.random.normal(avg_income,       std_income,      size=(n_simulations, n_months))
    monthly_expense = np.random.normal(stressed_expense, stressed_std_exp, size=(n_simulations, n_months))

    # Clamp negatives to zero — you can't have negative income/expense
    monthly_income  = np.clip(monthly_income,  0, None)
    monthly_expense = np.clip(monthly_expense, 0, None)

    net_cash_flow   = monthly_income - monthly_expense   # (n_simulations, n_months)
    cumulative_cash = np.cumsum(net_cash_flow, axis=1)   # running balance

    # ── Going-concern survival (Step 3) ───────────────────────────────────────
    # A simulation survives if its final cumulative cash balance is above zero
    # — i.e. the entity maintained positive cash over the entire forecast horizon.
    final_balances       = cumulative_cash[:, -1]
    survived             = final_balances > 0                      # bool array
    n_survived           = int(survived.sum())
    survival_probability = (n_survived / n_simulations) * 100     # explicit formula

    # Risk level thresholds
    if survival_probability >= 70:
        risk_level = "Low"
        risk_color = "#4ade80"   # green
    elif survival_probability >= 40:
        risk_level = "Medium"
        risk_color = "#fcd34d"   # amber
    else:
        risk_level = "High"
        risk_color = "#f87171"   # red

    # 20 sample paths for visualisation
    sample_indices = np.random.choice(n_simulations, size=min(20, n_simulations), replace=False)
    sample_paths   = pd.DataFrame(
        cumulative_cash[sample_indices, :],
        columns=[f"Month {m+1}" for m in range(n_months)],
    )

    return {
        "survival_probability":    round(survival_probability, 2),
        "risk_level":              risk_level,
        "risk_color":              risk_color,
        "sample_paths":            sample_paths,
        "final_balances":          final_balances,
        "avg_monthly_income":      round(avg_income,       2),
        "avg_monthly_expense":     round(stressed_expense, 2),  # stressed value shown in UI
        "avg_monthly_expense_base": round(avg_expense,     2),  # pre-stress, for methodology note
        "expense_multiplier":      round(expense_multiplier, 4),
        "n_simulations":           n_simulations,
    }


def _empty_result() -> dict:
    return {
        "survival_probability":     None,
        "risk_level":               "Unknown",
        "risk_color":               "#6b7280",
        "sample_paths":             pd.DataFrame(),
        "final_balances":           np.array([]),
        "avg_monthly_income":       0.0,
        "avg_monthly_expense":      0.0,
        "avg_monthly_expense_base": 0.0,
        "expense_multiplier":       1.0,
        "n_simulations":            0,
    }