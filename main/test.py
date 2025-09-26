from firebase_client import db
from datetime import datetime

doc_ref = db.collection("test").document("hello")
doc_ref.set({
    "msg": "Hello Firestore!",
    "timestamp": datetime.utcnow().isoformat()
})

print("✅ Wrote test doc to Firestore")
