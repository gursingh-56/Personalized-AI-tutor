def evaluate_quiz(state: dict) -> dict:
    quiz = state.get("last_quiz")
    user_answers = state.get("user_answers")
    level = state.get("current_level", "beginner")

    results, incorrect, correct_count = [], [], 0

    for i, q in enumerate(quiz["questions"]):
        user_answer = user_answers[i]
        correct_answer = q["correct_answer"]
        is_correct = user_answer == correct_answer

        if is_correct:
            correct_count += 1
        else:
            incorrect.append(q)

        results.append({
            "question": q["question"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

    score = correct_count / len(quiz["questions"]) * 100
    print(f"\nYour score: {score:.2f}%")

    state["review_needed"] = incorrect
    state.setdefault("profile", {})["level"] = level
    state["last_results"] = results
    state.setdefault("quiz_history", []).append({
        "score": score,
        "level": level,
        "results": results
    })

    return state
