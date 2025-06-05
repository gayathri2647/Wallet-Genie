# This is for test purpose

import pandas as pd
import firebase_admin 
from firebase_admin import credentials, firestore 
from datetime import datetime
import uuid
import sys
# to run python import_csv.py 3GAvtAHRXzOGf2LRhDmWhrPhJxI3
# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def import_transactions(csv_path, user_id):
    """Import transactions from CSV to Firebase"""
    print(f"Reading CSV file: {csv_path}")
    
    # Read CSV file
    df = pd.read_csv(csv_path)
    
    # Fix missing category in last row
    df['category'] = df['category'].fillna('Interest')
    
    # Convert date format (MM/DD/YYYY to YYYY-MM-DD)
    # df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
    
    # Add timestamps for created_at and updated_at
    now = datetime.now().isoformat()
    df['created_at'] = now
    df['updated_at'] = now
    
    # Add unique IDs
    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    
    # Convert to list of dictionaries
    transactions = df.to_dict('records')
    
    print(f"Importing {len(transactions)} transactions for user {user_id}")
    
    # Add transactions to Firestore in batches
    batch_size = 400  # Firestore has a limit of 500 operations per batch
    batches = [transactions[i:i+batch_size] for i in range(0, len(transactions), batch_size)]
    
    total_added = 0
    for batch_items in batches:
        batch = db.batch()
        for tx in batch_items:
            # Create a document reference with the UUID
            doc_ref = db.collection("users").document(user_id).collection("transactions").document(tx['id'])
            batch.set(doc_ref, tx)
        
        # Commit the batch
        batch.commit()
        total_added += len(batch_items)
        print(f"Added {total_added} transactions so far...")
    
    print(f"Successfully imported {total_added} transactions for user {user_id}")
    return total_added

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_csv.py <user_id>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    csv_path = "db/financial_transactions.csv"
    
    import_transactions(csv_path, user_id)