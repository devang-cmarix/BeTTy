def generate_gap_analysis(
        aspiration,
        baseline,
        aspiration_input=None
):
    aspiration_input = aspiration_input or {}

    blockers = []

    blockers.extend(
        baseline.get("mindsets", [])
    )

    blockers.extend(
        baseline.get("obstacles", [])
    )

    blockers.extend(
        baseline.get("external_factors", [])
    )

    force = aspiration_input.get("force", "your aspiration")
    issue = aspiration_input.get("issue", "your current challenge")
    feelings = baseline.get("feelings", [])
    motivations = baseline.get("motivations", [])
    values = baseline.get("values", [])
    daily_commitment = baseline.get("daily_commitment_minutes", 0)

    current_summary = (
        f"You are currently navigating {issue} while working on {force}. "
        f"Your attitude score is {baseline.get('attitude_score', 0)}, effort score is "
        f"{baseline.get('effort_score', 0)}, and motivation score is "
        f"{baseline.get('motivation_score', 0)}. "
        f"{'You described feeling ' + ', '.join(feelings) + '. ' if feelings else ''}"
        f"{'Your main blockers include ' + ', '.join(blockers[:4]) + '. ' if blockers else ''}"
        f"{'Your values of ' + ', '.join(values[:3]) + ' can support steady progress. ' if values else ''}"
        f"You are willing to invest {daily_commitment} minutes per day."
    )

    desired_summary = (
        f"In your desired future state, you are moving toward: {aspiration} "
        f"{'Your motivation is fueled by ' + ', '.join(motivations[:2]) + '. ' if motivations else ''}"
        f"By using your daily commitment and working around your blockers, you can create a more supportive "
        f"path from your current state to your aspiration."
    )

    success_criteria = [
        f"Invest {daily_commitment} minutes per day toward this aspiration",
        "Reduce the impact of your top blockers during daily practice",
        "Use your selected values to stay aligned when motivation dips",
        "Build consistency within your preferred time ranges",
    ]

    return {
        "aspiration": aspiration,
        "from_title": f"From {issue} in {force}",
        "to_title": f"To Empowered {force} Journey",
        "current_state": current_summary,
        "desired_state": desired_summary,
        "where_i_am": current_summary,
        "where_i_want_to_be": desired_summary,
        "blockers": blockers,
        "obstacles": blockers,
        "my_obstacles": blockers,
        "strengths": baseline.get(
            "values",
            []
        ),
        "success_criteria": success_criteria,
        "my_success_criteria": success_criteria,
        "daily_commitment":
            daily_commitment
    }
