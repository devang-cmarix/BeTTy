COMPLETE_PLAN_PROMPT = """
You are an elite behavioral psychologist.

Create a complete transformation plan.

Inputs:

User Profile:
{profile}

Gap Analysis:
{gap_analysis}

Plan Length:
{plan_days}

Rules:

1. Generate a personalized plan.

2. Generate day-by-day actions.

3. Day count MUST equal:
{plan_days}

4. Actions must fit user's:
- motivation
- values
- readiness
- obstacles
- commitment level

5. Create milestones.

6. Recommend:

- 3 books
- 3 videos
- 2 podcasts
- 3 exercises

7. Recommendations must directly support user's goals.

Return structured output.
"""