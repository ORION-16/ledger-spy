import pandas as pd


def compute_readiness_score(df: pd.DataFrame) -> dict:
    null_avg = df.isnull().mean().mean() * 100 if len(df.columns) else 0.0
    dup_pct = (df.duplicated().sum() / len(df)) * 100 if len(df) else 0.0
    score = max(0.0, 100.0 - (null_avg + dup_pct))
    return {
        "score": score,
        "null_pct": null_avg,
        "dup_pct": dup_pct,
        "col_count": len(df.columns),
    }
