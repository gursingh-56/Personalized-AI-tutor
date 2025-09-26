import json
import re
from datetime import datetime

def timestamp_now():
    return datetime.utcnow().isoformat() + "Z"

def clean_llm_output(content: str) -> str:
    """
    Remove code fences and extract a top-level JSON object if possible.
    """
    raw = content.strip()
    # remove triple-backticks markers if present
    raw = raw.replace("```json", "").replace("```", "").strip()
    # try to extract {...}
    m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    return m.group(0) if m else raw

def safe_json_parse(text: str):
    return json.loads(text)
