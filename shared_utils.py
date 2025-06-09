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

def delete_all_transactions(db, uid):
    """Delete all transactions for a user"""
    tx_ref = db.collection("users").document(uid).collection("transactions")
    batch = db.batch()
    
    # Get all transactions
    docs = tx_ref.stream()
    count = 0
    
    # Firestore batches are limited to 500 operations
    for doc in docs:
        batch.delete(tx_ref.document(doc.id))
        count += 1
        
        # If we reach 450 operations, commit the batch and start a new one
        if count >= 450:
            batch.commit()
            batch = db.batch()
            count = 0
    
    # Commit any remaining operations
    if count > 0:
        batch.commit()
    
    return True

def get_budget(db, uid):
    """Get user budget data from Firestore"""
    doc_ref = db.collection("users").document(uid).collection("budget").document("current")
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return {
        "monthly_income": 0,
        "categories": {}
    }

def update_budget(db, uid, budget_data):
    """Update budget data in Firestore"""
    doc_ref = db.collection("users").document(uid).collection("budget").document("current")
    doc_ref.set(budget_data, merge=True)
    return True

def get_goals(db, uid):
    """Get user financial goals from Firestore"""
    goals_ref = db.collection("users").document(uid).collection("goals").stream()
    goals = []
    for doc in goals_ref:
        goal_data = doc.to_dict()
        goal_data["id"] = doc.id
        goals.append(goal_data)
    return goals

def add_goal(db, uid, goal_data):
    """Add a new financial goal to Firestore"""
    goals_ref = db.collection("users").document(uid).collection("goals")
    goals_ref.add(goal_data)
    return True

def update_goal(db, uid, goal_id, goal_data):
    """Update an existing financial goal in Firestore"""
    goal_ref = db.collection("users").document(uid).collection("goals").document(goal_id)
    goal_ref.update(goal_data)
    return True

def delete_goal(db, uid, goal_id):
    """Delete a financial goal from Firestore"""
    goal_ref = db.collection("users").document(uid).collection("goals").document(goal_id)
    goal_ref.delete()
    return True