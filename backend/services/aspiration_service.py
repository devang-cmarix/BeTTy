from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(
    api_key=OPENAI_API_KEY
)


def generate_aspiration(payload):
    root_causes = ", ".join(payload.root_causes)

    prompt = f"""
Write a SMART goal for someone who wants to improve their {payload.force}
but is struggling with {payload.issue}
which is caused by the root issue of {root_causes}.

Use plain text.

Do not tell me what actions to take.
Do not explain how to solve the problem.

Instead summarize my aspirations and describe
the positive outcomes I could realize.

Requirements:
- Maximum 500 characters
- Timeframe between 30 and 90 days
- Positive
- Inspirational
- Concise
- Similar style to:

"I want a calm, focused mind and to feel more confident in how I see myself.
Over the next 60 days, I will build stronger focus, quieter self-talk,
and a growing sense of self-worth, allowing me to think clearly,
stay present, and approach each day with confidence and inner stability."
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are an aspiration writer.

Return only the aspiration text.

Do not use bullet points.
Do not use markdown.
Do not provide explanations.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip() # type: ignore
