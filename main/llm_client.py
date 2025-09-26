import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_llm(model=None, temperature=None):
    model = model or "gemini-2.5-flash"
    temperature = 0.1 if temperature is None else temperature
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set in environment (.env).")
    return ChatGoogleGenerativeAI(model=model, temperature=temperature, google_api_key=GOOGLE_API_KEY)
