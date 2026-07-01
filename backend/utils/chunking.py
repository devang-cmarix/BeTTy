def build_chunks(plan_days: int):

    if plan_days <= 45:
        return [(1, plan_days)]

    if plan_days <= 60:
        return [
            (1, 30),
            (31, plan_days)
        ]

    return [
        (1, 30),
        (31, 60),
        (61, plan_days)
    ]