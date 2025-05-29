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
from pages.Settings import get_categories # <--- IMPORTANT CHANGE: Import get_categories from Settings

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

# Custom CSS
st.markdown("""
    <style>
    .prediction-card {
        background-color: #e8f4f9;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #4682b4;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Add New Transaction 💰")

# Fetch user-defined categories
user_categories = get_categories(user_id)

# Default categories to fall back on if the user hasn't defined any custom ones
default_expense_categories = ["Food & Dining", "Transportation", "Shopping", "Entertainment", "Bills & Utilities", "Education", "Health", "Personal Care", "Others"]
default_income_categories = ["Salary", "Freelance", "Investment Returns", "Gift", "Bonus", "Rental Income", "Refunds", "Other Income"]

expense_categories = user_categories.get("expense", [])
if not expense_categories: # If no custom expense categories, use defaults
    expense_categories = default_expense_categories

income_categories = user_categories.get("income", [])
if not income_categories: # If no custom income categories, use defaults
    income_categories = default_income_categories

# Transaction form
with st.form("transaction_form"):
    transaction_type = st.selectbox("Type", ["Expense", "Income"])

    # Dynamically change category options based on transaction type
    if transaction_type == "Expense":
        category_options = expense_categories
    else:
        category_options = income_categories

    category =  st.selectbox("Category", category_options) # <--- IMPORTANT CHANGE: Use dynamic categories

    description = st.text_area("Description", height=90, placeholder="Enter transaction description")

    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Amount ($)", min_value=1.00, format="%0.2f")
    with col2:
        date = st.date_input("Date", value=datetime.now())

    submit_button = st.form_submit_button("Add Transaction")

# Handle form submission
if submit_button:
    if description and amount:

        # Display prediction (using selected category for now)
        st.markdown(f"""
            <div class="prediction-card">
            <h4>🤖 AI Category Prediction</h4>
            Category: <b>{category}</b><br>
            </div>
        """, unsafe_allow_html=True)

        st.success("Transaction added successfully!")

        tx_id = str(uuid.uuid4())  # Unique transaction ID
        doc_ref = db.collection("users").document(user_id).collection("transactions").document(tx_id)
        doc_ref.set({
            "description": description,
            "amount": amount,
            "date": date.strftime("%m/%d/%Y"),
            "type": transaction_type,
            "category": category
        })
    else:
        st.error("Please fill in all required fields.")

def get_user_transactions_for_download(uid): # Renamed to avoid confusion with cached version
    tx_ref = db.collection("users").document(uid).collection("transactions").stream()
    return [tx.to_dict() for tx in tx_ref]

tx_data = get_user_transactions_for_download(user_id)
df = pd.DataFrame(tx_data)


# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))