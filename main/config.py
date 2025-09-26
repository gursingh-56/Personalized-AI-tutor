from pathlib import Path

# Storage / Firebase toggle
FIREBASE_ENABLED = False
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"  # only used if FIREBASE_ENABLED = True

# Data paths (used when FIREBASE_ENABLED == False)
DATA_DIR = Path("data")
PROFILES_DIR = DATA_DIR / "profiles"
CHATS_DIR = DATA_DIR / "chats"
QUIZZES_DIR = DATA_DIR / "quizzes"
RESULTS_DIR = DATA_DIR / "results"
REVIEWS_DIR = DATA_DIR / "reviews"
SYLLABI_DIR = DATA_DIR / "syllabi"

# LLM config
QUIZ_MODEL = "gemini-1.5-flash-latest"
QUIZ_TEMPERATURE = 0.1

# Quiz settings
OPTION_LABELS = ["A", "B", "C", "D"]
NUM_QUIZ_QUESTIONS = 10
