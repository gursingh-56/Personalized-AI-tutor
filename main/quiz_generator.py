from langchain_core.messages import HumanMessage
from llm_client import get_llm

from utils import clean_llm_output, safe_json_parse
from config import OPTION_LABELS

llm = get_llm()

def generate_quiz(state: dict) -> dict:
    topic = state.get("current_topic", "general")
    level = state.get("current_level", "beginner")
    preferences = state.get("preferences", {})

    prompt = f"""
    Based on the user's learning preferences: {preferences},
    generate a quiz (10 questions) on topic: {topic}.
    Difficulty: {level}.
    JSON Format:
    {{
        "questions": [
            {{
                "question": "...",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "B"
            }}
        ]
    }}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    parsed = safe_json_parse(clean_llm_output(response.content))
    state["last_quiz"] = parsed
    return state

def ask_user_questions(state: dict) -> dict:
    quiz = state["last_quiz"]
    user_answers = []

    for i, q in enumerate(quiz["questions"]):
        print(f"\nQ{i+1}: {q['question']}")
        for j, opt in enumerate(q["options"]):
            print(f"{OPTION_LABELS[j]}. {opt}")

        while True:
            ans = input("Your answer (A/B/C/D): ").strip().upper()
            if ans in OPTION_LABELS[:len(q["options"])]:
                break
            print("Invalid input. Try again.")

        user_answers.append(q["options"][OPTION_LABELS.index(ans)])

    state["user_answers"] = user_answers
    state["quiz_mode"] = "evaluate"
    return state
