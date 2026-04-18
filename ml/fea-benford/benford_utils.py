def get_benford_risk(score: float) -> str:
    if score > 50:
        return "HIGH"
    elif score > 25:
        return "MEDIUM"
    else:
        return "LOW"


def generate_benford_insight(score: float, suspicious_digits=None) -> str:
    if score < 25:
        return "Transaction amounts follow natural Benford distribution."

    elif score < 50:
        return "Moderate deviation detected. Some digits show unusual frequency."

    else:
        return "High deviation detected. Possible fabricated or manipulated transaction amounts."


def build_benford_result(summary: dict) -> dict:
    score = summary["overall_deviation_score"]

    return {
        "benford_score": score,
        "benford_risk": get_benford_risk(score),
        "insight": generate_benford_insight(score)
    }