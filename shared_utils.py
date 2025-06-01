# shared_utils.py
# Shared utilities for WalletGenie app to ensure consistent data access across pages

def get_categories(db, uid):
    """Get user categories directly from Firestore without caching"""
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("categories", {"expense": [], "income": []})
    return {"expense": [], "income": []}

def update_categories_firestore(db, uid, categories_data):
    """Update categories in Firestore"""
    doc_ref = db.collection("users").document(uid)
    doc_ref.set({"categories": categories_data}, merge=True)