def build_chunks(plan_days: int):
    """Split a long plan into smaller chunks so the LLM can reliably produce every day."""

    if plan_days <= 30:
        return [(1, plan_days)]

    chunk_size = 15 if plan_days <= 90 else 20
    chunks = []
    start = 1
    while start <= plan_days:
        end = min(plan_days, start + chunk_size - 1)
        chunks.append((start, end))
        start = end + 1
    return chunks
