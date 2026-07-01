import json
from pathlib import Path

from openai import OpenAI

from config import OPENAI_API_KEY

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "forces.json"
client = OpenAI(api_key=OPENAI_API_KEY)

with DATA_FILE.open("r", encoding="utf-8") as f:
    DATA = json.load(f)


def get_all_forces():
    return [
        {
            "slug": force["slug"],
            "label": force["label"]
        }
        for force in DATA["forces"]
    ]


def get_force(slug: str):
    for force in DATA["forces"]:
        if force["slug"] == slug:
            return force

    return None


def get_issue_options(slug: str):

    force = get_force(slug)

    if not force:
        return None

    return {
        "question": force["question"],
        "options": force["details"]
    }
    
    
def get_root_causes(slug: str, detail: str):
    force = get_force(slug)

    if not force:
        return None

    return {
        "question": force["root_question"],
        "root_causes":
            force["root_causes_by_detail"].get(detail, [])
    }


def classify_force(user_input: str):
    forces = get_all_forces()
    allowed_slugs = {force["slug"] for force in forces}
    force_options = "\n".join(
        f'- {force["slug"]}: {force["label"]}'
        for force in forces
    )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify the user's text into exactly one wellness force. "
                    "Return JSON only in this format: "
                    '{"slug":"one_allowed_slug","reason":"short reason"}'
                )
            },
            {
                "role": "user",
                "content": (
                    f"Allowed forces:\n{force_options}\n\n"
                    f"User text:\n{user_input}"
                )
            }
        ],
        temperature=0
    )

    raw_result = response.choices[0].message.content
    try:
        result = json.loads(raw_result)
    except json.JSONDecodeError:
        start = raw_result.find("{")
        end = raw_result.rfind("}") + 1
        result = json.loads(raw_result[start:end])
    slug = result.get("slug")

    if slug not in allowed_slugs:
        slug = "focus-mind"

    force = get_force(slug)

    return {
        "slug": slug,
        "label": force["label"],
        "reason": result.get("reason", "")
    }
