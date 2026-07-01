from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_gap_analysis(payload):

    prompt = f"""
You are an expert wellness coach.

Selected Force:
{payload.force}

Selected Issue:
{payload.detail}

Selected Root Causes:
{", ".join(payload.root_causes)}

Emotion:
{payload.emotion}

Value:
{payload.value}

Mindset:
{payload.mindset}

Obstacle:
{payload.obstacle}

Return JSON only.

Format:

{{
    "gap_summary":"",
    "limiting_beliefs":[],
    "strengths":[],
    "action_plan":[],
    "motivation_score":0,
    "encouragement":""
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a professional life coach."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content