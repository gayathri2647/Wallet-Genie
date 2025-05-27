import csv
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase with your service account key
cred = credentials.Certificate("firebase_key.json")  # Change this
firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

# CSV file path
csv_file_path = "db/yuvi_transactions.csv"  # Change this

# Your Firestore user UID
user_uid = "yugesh_demo_uid"

# Collection path: users/{user_uid}/transactions
collection_ref = db.collection("users").document(user_uid).collection("transactions")

# Read the CSV and add each row as a document with an auto ID
with open(csv_file_path, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        try:
            # Convert amount to int
            row["amount"] = float(row["amount"])
            # Upload document with auto-generated ID
            collection_ref.add(row)
        except Exception as e:
            print(f"Error with row {row}: {e}")

print("✅ All transactions uploaded successfully with auto-generated IDs.")
