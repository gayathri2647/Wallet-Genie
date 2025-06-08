import uuid
import streamlit as st
import sys
import os
from datetime import datetime
from firebase_init import init_firestore
import pandas as pd

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from shared_utils import get_categories  # Import from shared_utils

# Check authentication
check_auth()

db = init_firestore()

user_id = st.session_state.user_id

# Page config
st.set_page_config(
    page_title="Add Transaction - WalletGenie",
    page_icon="💰",
    layout="centered"
)


st.title("Add New Transaction 💰")

# Fetch user-defined categories directly from Firestore (no caching)
user_categories = get_categories(db, user_id)

# Default categories to fall back on if the user hasn't defined any custom ones
default_expense_categories = ["Food & Dining", "Transportation", "Shopping", "Entertainment", "Bills & Utilities", "Education", "Health", "Personal Care", "Others"]
default_income_categories = ["Salary", "Freelance", "Investment Returns", "Gift", "Bonus", "Rental Income", "Refunds", "Other Income"]
# type_categories = ["Pick type...","Expense", "Income"]

expense_categories = user_categories.get("expense", [])
if not expense_categories: # If no custom expense categories, use defaults
    expense_categories = default_expense_categories

income_categories = user_categories.get("income", [])
if not income_categories: # If no custom income categories, use defaults
    income_categories = default_income_categories




with st.container():


    transaction_type = st.selectbox("Type", ["Expense", "Income"], key="transaction_type")
    # Dynamically set category options
    category_options = expense_categories if transaction_type == "Expense" else income_categories
    # Add "Others" option if not already present
    if "Others" not in category_options:
        category_options = list(category_options) + ["Others"]
        
    category = st.selectbox("Category", category_options, key="category")

    # Show text input for custom category when "Others" is selected
    custom_category = None
    if category == "Others":
        custom_category = st.text_input("Enter custom category", key="custom_category")

    description = st.text_area("Description", height=90, placeholder="Enter transaction description")

    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Amount (₹)", min_value=1.00, format="%0.2f")
    with col2:
        date = st.date_input("Date", value=datetime.now())

    submit_button = st.button("Add Transaction")

# Handle form submission
if submit_button:
    if description and amount:
        # Use custom category if "Others" was selected and a custom category was entered
        final_category = custom_category if category == "Others" and custom_category else category
        
        # Don't submit if "Others" was selected but no custom category was entered
        if category == "Others" and not custom_category:
            st.error("Please enter a custom category name.")
        else:
            tx_id = str(uuid.uuid4())  # Unique transaction ID
            doc_ref = db.collection("users").document(user_id).collection("transactions").document(tx_id)
            doc_ref.set({
                "description": description,
                "amount": amount,
                "date": date.strftime("%m/%d/%Y"),
                "type": transaction_type,
                "category": final_category
            })
            st.success("Transaction added successfully!")
    else:
        st.error("Please fill in all required fields.")

def get_user_transactions_for_download(uid):
    tx_ref = db.collection("users").document(uid).collection("transactions").stream()
    return [tx.to_dict() for tx in tx_ref]

tx_data = get_user_transactions_for_download(user_id)
df = pd.DataFrame(tx_data)

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))