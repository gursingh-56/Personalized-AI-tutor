from langchain_core.messages import HumanMessage
from llm_client import get_llm
import json

llm = get_llm()

def review_incorrect(state: dict) -> dict:
    incorrect = state.get("review_needed", [])
    if not incorrect:
        print("Nothing to review.")
        return state

    prompt = f"""
    The user got these wrong:
    {json.dumps(incorrect, indent=2)}

    For each one:
    - Explain the correct answer simply
    - Add a short explanation
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    print("\nReview:\n", response.content)
    return state
