import os
import sys

# Configure sys.path to include project root for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from llm_config import llm
from langchain_core.prompts import ChatPromptTemplate
from schemas.gap_analysis_schema import GapAnalysisSchema

async def generate_gap_analysis(
        aspiration,
        baseline,
        aspiration_input=None
):
    aspiration_input = aspiration_input or {}

    blockers = []
    blockers.extend(baseline.get("mindsets", []))
    blockers.extend(baseline.get("obstacles", []))
    blockers.extend(baseline.get("external_factors", []))

    force = aspiration_input.get("force", "your aspiration")
    issue = aspiration_input.get("issue", "your current challenge")
    feelings = baseline.get("feelings", [])
    motivations = baseline.get("motivations", [])
    values = baseline.get("values", [])
    daily_commitment = baseline.get("daily_commitment_minutes", 0)

    profile_info = {
        "force": force,
        "issue": issue,
        "feelings": feelings,
        "motivations": motivations,
        "values": values,
        "daily_commitment_minutes": daily_commitment,
        "attitude_score": baseline.get("attitude_score", 0),
        "effort_score": baseline.get("effort_score", 0),
        "motivation_score": baseline.get("motivation_score", 0),
        "mindsets": baseline.get("mindsets", []),
        "obstacles": baseline.get("obstacles", []),
        "external_factors": baseline.get("external_factors", []),
        "learning_preferences": baseline.get("learning_preferences", []),
        "notes": baseline.get("notes", "")
    }

    prompt = ChatPromptTemplate.from_template("""
You are a behavioral psychologist.
Analyze the user profile and baseline to perform a Gap Analysis.

Aspiration:
{aspiration}

User Baseline and Inputs:
{profile}

Return a structured JSON with:
1. "where_i_am": A summary (100-150 words) of the user's current baseline, feelings, and blockers.
2. "where_i_want_to_be": A summary (100-150 words) of the user's desired state, goals, and what fuels them.
3. "my_obstacles": A list of exactly 4 specific obstacles/blockers based on their baseline.
4. "my_success_criteria": A list of exactly 4 specific success criteria.
   - The first 2 items MUST start with "STOP " (e.g. "STOP checking social media immediately when waking up").
   - The next 2 items MUST start with "START " (e.g. "START writing down three core priorities every morning").
   - These criteria must be tailored specifically to the user's aspiration: {aspiration}.
""")

    structured_llm = llm.with_structured_output(GapAnalysisSchema)
    chain = prompt | structured_llm

    try:
        result = await chain.ainvoke({
            "aspiration": aspiration,
            "profile": str(profile_info)
        })
        res_data = result.model_dump()
        where_i_am = res_data["where_i_am"]
        where_i_want_to_be = res_data["where_i_want_to_be"]
        my_obstacles = res_data["my_obstacles"]
        my_success_criteria = res_data["my_success_criteria"]
    except Exception as e:
        # Fallback to procedural generation if LLM call fails
        print(f"LLM gap analysis failed: {e}. Falling back to procedural.")
        where_i_am = (
            f"You are currently navigating {issue} while working on {force}. "
            f"Your attitude score is {baseline.get('attitude_score', 0)}, effort score is "
            f"{baseline.get('effort_score', 0)}, and motivation score is "
            f"{baseline.get('motivation_score', 0)}. "
            f"{'You described feeling ' + ', '.join(feelings) + '. ' if feelings else ''}"
            f"{'Your main blockers include ' + ', '.join(blockers[:4]) + '. ' if blockers else ''}"
            f"You are willing to invest {daily_commitment} minutes per day."
        )
        where_i_want_to_be = (
            f"In your desired future state, you are moving toward: {aspiration} "
            f"{'Your motivation is fueled by ' + ', '.join(motivations[:2]) + '. ' if motivations else ''}"
        )
        my_obstacles = blockers
        my_success_criteria = [
            f"STOP ignoring the obstacle of {blockers[0] if len(blockers) > 0 else 'distractions'}",
            f"STOP spending time on activities that don't support your {force}",
            f"START dedicating {daily_commitment} minutes daily to {force}",
            f"START leveraging your values of {', '.join(values[:2]) if values else 'consistency'} to overcome obstacles"
        ]

    return {
        "aspiration": aspiration,
        "from_title": f"From {issue} in {force}",
        "to_title": f"To Empowered {force} Journey",
        "current_state": where_i_am,
        "desired_state": where_i_want_to_be,
        "where_i_am": where_i_am,
        "where_i_want_to_be": where_i_want_to_be,
        "blockers": my_obstacles,
        "obstacles": my_obstacles,
        "my_obstacles": my_obstacles,
        "strengths": baseline.get("values", []),
        "success_criteria": my_success_criteria,
        "my_success_criteria": my_success_criteria,
        "daily_commitment": daily_commitment
    }

