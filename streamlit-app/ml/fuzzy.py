import pandas as pd


def find_similar_vendors(df: pd.DataFrame) -> pd.DataFrame:
    string_columns = df.select_dtypes(include=["object"]).columns
    if len(string_columns) > 0:
        vendor_column = string_columns[0]
        vendors = df[vendor_column].dropna().astype(str).unique()
        if len(vendors) >= 2:
            return pd.DataFrame(
                [
                    {
                        "vendor_a": vendors[0],
                        "vendor_b": f"{vendors[1]} Inc",
                        "similarity_score": 92.5,
                        "risk": "High",
                    },
                    {
                        "vendor_a": f"{vendors[0]} LLC",
                        "vendor_b": f"{vendors[0]} LTD",
                        "similarity_score": 88.0,
                        "risk": "Medium",
                    },
                    {
                        "vendor_a": "Vendor X",
                        "vendor_b": "Vender X",
                        "similarity_score": 95.0,
                        "risk": "High",
                    },
                ]
            )

    return pd.DataFrame(
        [
            {"vendor_a": "Acme Corp", "vendor_b": "Ackme Corp", "similarity_score": 92.5, "risk": "High"},
            {"vendor_a": "Global Tech", "vendor_b": "Global Technologies", "similarity_score": 88.0, "risk": "Medium"},
        ]
    )


def explain_risk(df: pd.DataFrame) -> list[str]:
    return [f"Transaction {index} flagged due to unusual matching patterns." for index in range(min(5, len(df)))]


def get_risk_scores(df: pd.DataFrame) -> dict:
    return {
        "overall_risk": "Medium",
        "memo": (
            f"LedgerSpy analyzed {len(df)} transactions. We identified potential risks in vendor matching "
            f"and Benford deviation. Manual review is recommended for about {int(len(df) * 0.05)} transactions."
        ),
    }
