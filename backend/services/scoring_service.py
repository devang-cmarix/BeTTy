def calculate_readiness_score(
        attitude,
        effort,
        motivation
):

    score = round(
        (attitude + effort + motivation) / 3,
        2
    )

    if score <= 3:
        level = "Low"

    elif score <= 7:
        level = "Moderate"

    else:
        level = "High"

    return {
        "score": score,
        "level": level
    }