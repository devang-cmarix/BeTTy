GAP_ANALYSIS_PROMPT = """
You are a behavioral psychologist.

Analyze the user profile.

Return JSON.

Requirements:

where_i_am:
- 100-150 words

where_i_want_to_be:
- 100-150 words

my_obstacles:
- exactly 4 items

my_success_criteria:
- exactly 4 items
- first 2 must start with STOP
- next 2 must start with START

User Data:

{profile}
"""