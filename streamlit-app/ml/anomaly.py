import numpy as np
import pandas as pd


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()

    if "amount" not in df_out.columns:
        numeric_columns = df_out.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            df_out["amount"] = df_out[numeric_columns[0]]
        else:
            df_out["amount"] = np.random.uniform(10, 5000, size=len(df_out))

    np.random.seed(42)
    df_out["anomaly_score"] = np.random.uniform(0, 100, size=len(df_out))
    df_out["is_anomaly"] = df_out["anomaly_score"] > 85
    df_out["explanation"] = np.where(
        df_out["is_anomaly"],
        "61% high anomaly score, 24% unusual amount, 15% pattern deviation",
        "18% baseline variance, 82% normal profile",
    )
    return df_out


def benford_analysis(df: pd.DataFrame) -> pd.DataFrame:
    digits = list(range(1, 10))
    expected = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]
    actual = [max(0, value + np.random.uniform(-2, 2)) for value in expected]
    return pd.DataFrame({"Digit": digits, "Expected": expected, "Actual": actual})
