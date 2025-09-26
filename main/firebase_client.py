import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Load service account key
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# ──────────────────────────────
# Example Helper Functions
# ──────────────────────────────
def save_user_profile(user_id: str, name: str, preferences: dict, syllabus: dict, current_topic: str, current_level: str, first_time: bool):
    profile_data = {
        "name": name,
        "preferences": preferences,
        "syllabus": syllabus,
        "current_topic": current_topic,
        "current_level": current_level,
        "first_time": first_time,
        "timestamp": datetime.utcnow().isoformat()
    }
    db.collection("users").document(user_id).set(profile_data)
    print(f"✅ User profile saved for {user_id}")


def get_user_profile(user_id: str):
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        return doc.to_dict()
    return None

def save_chat(user_id: str, message: dict):
    message["timestamp"] = datetime.utcnow().isoformat()
    db.collection("users").document(user_id).collection("chats").add(message)
    print(f"💬 Chat message saved for {user_id}")

def get_chat_history(user_id: str):
    chats = db.collection("users").document(user_id)\
        .collection("chats").order_by("timestamp").stream()
    return [chat.to_dict() for chat in chats]

def save_quiz(user_id: str, quiz: dict):
    quiz["timestamp"] = datetime.utcnow().isoformat()
    db.collection("users").document(user_id).collection("quizzes").add(quiz)
    print(f"✅ Quiz saved for {user_id}")

def get_quiz_history(user_id: str):
    quizzes = db.collection("users").document(user_id)\
        .collection("quizzes").order_by("timestamp").stream()
    return [q.to_dict() for q in quizzes]
