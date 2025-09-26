# main.py
import sys
from llm_client import get_llm
from storage import StorageManager
from nodes import (
    get_or_create_profile,
    generate_syllabus,
    generate_quiz,
    ask_user_questions,
    evaluate_quiz,
    review_incorrect,
)
from utils import timestamp_now
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import json


# ──────────────────────────────────────
# System prompt builder
# ──────────────────────────────────────
def build_system_prompt(state):
    pref = state.get("preferences", {})
    name = state.get("name", "User")
    topic = state.get("current_topic", "Unknown")
    level = state.get("current_level", "Unknown")
    text = f"""
You are a personalized AI tutor for {name}.
Preferences: {json.dumps(pref, indent=2)}
Topic: {topic}
Level: {level}
Be concise, actionable, and teach one idea at a time.
"""
    return {"role": "system", "content": text.strip()}


def convert_to_langchain_messages(history):
    msgs = []
    for m in history:
        role = m.get("role")
        if role == "user":
            msgs.append(HumanMessage(content=m["content"]))
        elif role == "assistant":
            msgs.append(AIMessage(content=m["content"]))
        elif role == "system":
            msgs.append(SystemMessage(content=m["content"]))
    return msgs


# ──────────────────────────────────────
# Main program
# ──────────────────────────────────────
def main():
    llm = get_llm()
    storage = StorageManager()
    state = {}

    # 1) Load or create user profile
    state = get_or_create_profile(state, llm, storage)
    user_id = state["name"]

    # 2) Ask topic & level
    state["current_topic"] = input("\n📘 What topic would you like to learn? ").strip()
    state["current_level"] = input("📗 Your level (Beginner, Intermediate, Advanced): ").strip() or "Beginner"

    # Generate syllabus and save full profile
    state = generate_syllabus(state, llm, storage)
    storage.save_user_profile(user_id, state)

    # 3) Quiz flow
    start_quiz = input("\nStart quiz now? (y/N): ").strip().lower()
    if start_quiz == "y":
        state = generate_quiz(state, llm, storage)
        state = ask_user_questions(state)
        state = evaluate_quiz(state, storage)
        state = review_incorrect(state, llm, storage)
        print("\n✅ Quiz + review complete.")

    # 4) Interactive chat loop
    chat_history = [build_system_prompt(state)]
    print("\nYou can chat with the tutor now. Commands: !quiz, !review, exit/q")

    while True:
        try:
            user_input = input("User: ").strip()
            if user_input.lower() in ("exit", "quit", "q"):
                storage.save_chat(user_id, chat_history)
                print("Goodbye — chat saved.")
                sys.exit(0)

            # Commands
            if user_input.startswith("!"):
                cmd = user_input[1:].strip().lower()
                if cmd == "quiz":
                    state = generate_quiz(state, llm, storage)
                    state = ask_user_questions(state)
                    state = evaluate_quiz(state, storage)
                    state = review_incorrect(state, llm, storage)
                    continue
                elif cmd == "review":
                    review_incorrect(state, llm, storage)
                    continue
                elif cmd == "help":
                    print("Commands: !quiz, !review, exit/q")
                    continue
                else:
                    print("❌ Unknown command.")
                    continue

            # Normal chat turn
            user_msg = {"role": "user", "content": user_input, "timestamp": timestamp_now()}
            chat_history.append(user_msg)
            storage.append_chat_message(user_id, user_msg)

            lc_messages = convert_to_langchain_messages(chat_history)
            resp = llm.invoke(lc_messages)
            assistant_text = resp.content
            assistant_msg = {"role": "assistant", "content": assistant_text, "timestamp": timestamp_now()}
            chat_history.append(assistant_msg)
            storage.append_chat_message(user_id, assistant_msg)

            print("Assistant:", assistant_text)

        except KeyboardInterrupt:
            print("\nInterrupted — saving chat and exiting.")
            storage.save_chat(user_id, chat_history)
            sys.exit(0)


if __name__ == "__main__":
    main()
