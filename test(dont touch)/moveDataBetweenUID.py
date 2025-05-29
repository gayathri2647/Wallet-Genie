import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate("path_to_your_admin_sdk.json")  #change it
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Replace with your old and new user IDs
old_uid = "tlvR8sCvoJa9ra4Yub9mOZ5zbfu2"  # demo UID
new_uid = "your_actual_firebase_uid"    # real UID (from login_user())

# Reference old and new transaction collections
old_trans_ref = db.collection("users").document(old_uid).collection("transactions")
new_trans_ref = db.collection("users").document(new_uid).collection("transactions")

# Get all documents from the old user's transactions
docs = old_trans_ref.stream()

for doc in docs:
    data = doc.to_dict()
    new_trans_ref.document(doc.id).set(data)

print("✅ All transaction data moved successfully.")
