# storage.py
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def timestamp_now():
    return datetime.datetime.utcnow().isoformat()


class StorageManager:
    def __init__(self, db=None):
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase-key.json")
            firebase_admin.initialize_app(cred)
        self.db = firestore.client() if db is None else db


    # ─── User Profile ─────────────────────────────
    def save_user_profile(self, user_id: str, state: dict):
        profile_data = {
            "name": state.get("name"),
            "preferences": state.get("preferences", {}),
            "syllabus": state.get("syllabus", {}),
            "current_topic": state.get("current_topic"),
            "current_level": state.get("current_level"),
            "first_time": state.get("first_time", False),
            "timestamp": timestamp_now(),
        }
        self.db.collection("users").document(user_id).set(profile_data, merge=True)
        print(f"✅ User profile saved for {user_id}")

    def get_user_profile(self, user_id: str):
        doc = self.db.collection("users").document(user_id).get()
        return doc.to_dict() if doc.exists else None

    # ─── Chat Messages ────────────────────────────
    def append_chat_message(self, user_id, message: dict):
        """Append a single chat message to Firestore with timestamp index"""
        try:
            chat_ref = (
                self.db.collection("users")
                .document(user_id)
                .collection("chats")
            )
            chat_ref.add(message)
            print(f"💾 Chat saved: {message['role']} - {message['content'][:30]}")
        except Exception as e:
            print("❌ Error appending chat:", e)

    def save_chat(self, user_id, chat_history: list):
        """Save entire chat as one document (backup on exit)"""
        try:
            doc_ref = (
                self.db.collection("users")
                .document(user_id)
                .collection("sessions")
                .document("latest_chat")
            )
            doc_ref.set({"chat_history": chat_history})
            print("💾 Entire chat session saved (backup).")
        except Exception as e:
            print("❌ Error saving full chat:", e)

    
    def get_chat_history(self, user_id: str):
        chats = self.db.collection("users").document(user_id)\
            .collection("chats").order_by("timestamp").stream()
        return [c.to_dict() for c in chats]


    # ─── Quizzes ─────────────────────────────────
    def save_quiz(self, user_id: str, quiz: dict):
        quiz = quiz.copy()
        quiz["timestamp"] = timestamp_now()
        self.db.collection("users").document(user_id).collection("quizzes").add(quiz)
        print(f"✅ Quiz saved for {user_id}")

    def get_quiz_history(self, user_id: str):
        quizzes = self.db.collection("users").document(user_id)\
            .collection("quizzes").order_by("timestamp").stream()
        return [q.to_dict() for q in quizzes]
