import json
import re
from langchain_core.messages import HumanMessage
from utils import clean_llm_output, safe_json_parse, timestamp_now
from config import OPTION_LABELS, NUM_QUIZ_QUESTIONS
from pathlib import Path

# NOTE: all functions accept llm and storage instances so there's no circular import.

# nodes/get_or_create_profile.py
from utils import timestamp_now

def get_or_create_profile(state: dict, llm, storage):
    user_id = input("Enter your name: ").strip()
    state["name"] = user_id

    profile = storage.get_user_profile(user_id)
    if profile:
        print(f"\n✅ Loaded existing learning profile for {user_id}.")
        state.update(profile)
        state["first_time"] = False
        return state

    # First-time user – ask learning preferences
    question_prompt = """
    Ask me 15 questions about my learning preferences...
    """
    response = llm.invoke([{"role": "user", "content": question_prompt}])
    questions = [q.strip() for q in response.content.split("\n") if q.strip()]
    
    answers = {}
    for idx, q in enumerate(questions, 1):
        print(f"Q{idx}. {q}")
        answers[q] = input("➤ ")

    analysis_prompt = f"""
    Based on responses, create a JSON-formatted learning profile.
    Responses: {answers}
    """
    analysis_resp = llm.invoke([{"role": "user", "content": analysis_prompt}])
    profile_json = analysis_resp.content  # assume JSON parse succeeds
    raw = profile_json.strip()

    # remove code block wrappers if any
    raw = re.sub(r"^```json", "", raw)
    raw = re.sub(r"```$", "", raw)

    # try to extract JSON if there's extra text
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        raw = match.group(0)

    # parse JSON safely
    try:
        profile_json = parse_llm_json(profile_json)
    except json.JSONDecodeError:
        print("❌ Failed to parse LLM output as JSON. Output was:\n", raw)
        raise

    state["preferences"] = profile_json
    state["first_time"] = True
    storage.save_user_profile(user_id, state)
    return state


def generate_syllabus(state, llm, storage):
    topic = state.get("current_topic")
    level = state.get("current_level")
    preferences = state.get("preferences", {})

    prompt = f"""
    Create a syllabus for topic: {topic}, level: {level}, for user with preferences: {preferences}
    """
    response = llm.invoke([{"role": "user", "content": prompt}])
    syllabus = response.content  # assume JSON parse
    syllabus_raw = llm.invoke([HumanMessage(content=prompt)]).content
    syllabus = parse_llm_json(syllabus_raw)
    state["syllabus"] = syllabus

    # Safely parse
    try:
        syllabus = parse_llm_json(syllabus)
    except json.JSONDecodeError:
        print("❌ Failed to parse LLM syllabus output. Raw output was:\n", raw)
        raise

    state["syllabus"] = syllabus
    storage.save_user_profile(state["name"], state)
    print(f"✅ Syllabus saved for {state['name']}")
    return state



def generate_quiz(state, llm, storage):
    topic = state.get("current_topic")
    level = state.get("current_level")
    preferences = state.get("preferences", {})

    prompt = f"""
    Generate a 10-question quiz for topic {topic}, level {level}, preferences {preferences}.
    Return JSON.
    """
    response = llm.invoke([{"role": "user", "content": prompt}])
    import json, re
    raw = response.content.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)

    if match:
        quiz = parse_llm_json(match.group(0))
    else:
        quiz = {}
    state["last_quiz"] = quiz
    return state

def ask_user_questions(state):
    quiz = state.get("last_quiz", {})
    user_answers = []
    for i, q in enumerate(quiz.get("questions", [])):
        print(f"\nQ{i+1}: {q['question']}")
        for idx, opt in enumerate(q["options"]):
            print(f"{chr(65+idx)}. {opt}")
        ans = input("Answer (A/B/C/D): ").strip().upper()
        user_answers.append(q["options"][ord(ans)-65])
    state["user_answers"] = user_answers
    return state



def evaluate_quiz(state: dict, storage):
    quiz = state.get("last_quiz")
    user_answers = state.get("user_answers", [])
    if not quiz or not user_answers or len(quiz.get("questions", [])) != len(user_answers):
        raise ValueError("Mismatch in questions and answers or missing data.")

    results = []
    correct_count = 0
    incorrect = []

    for i, q in enumerate(quiz["questions"]):
        correct_answer = q.get("correct_answer")
        user_answer = user_answers[i]
        is_correct = (user_answer == correct_answer)
        results.append({
            "question": q.get("question"),
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })
        if is_correct:
            correct_count += 1
        else:
            incorrect.append(q)

    score = correct_count / len(quiz["questions"]) * 100
    print(f"\nYour score: {score:.2f}%")

    state["last_results"] = results
    state["review_needed"] = incorrect
    storage.save("results", {"username": state.get("name"), "score": score, "results": results, "topic": state.get("current_topic")})
    return state


def review_incorrect(state, llm, storage):
    incorrect = [r for r in state.get("last_results", []) if not r["is_correct"]]
    if not incorrect:
        print("Nothing to review!")
        return state

    prompt = f"""
    Explain the correct answers for these questions: {incorrect}
    """
    resp = llm.invoke([{"role": "user", "content": prompt}])
    print("\nReview:\n", resp.content)
    return state


import json, re

def parse_llm_json(raw: str) -> dict:
    """Safely parse LLM output into JSON."""
    if not raw or raw.strip() == "":
        print("❌ LLM returned empty output.")
        return {}  # return empty dict instead of crashing

    raw = raw.strip()

    # Remove code block wrappers if any
    raw = re.sub(r"^```json", "", raw)
    raw = re.sub(r"```$", "", raw)

    # Extract JSON object from extra text
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        raw = match.group(0)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("❌ Failed to parse LLM output as JSON. Raw output was:\n", raw)
        return {}  # fallback to empty dict
