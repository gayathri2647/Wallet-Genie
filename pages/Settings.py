import streamlit as st
import sys
import os
import firebase_admin
from firebase_admin import firestore
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from firebase_init import init_firestore
from config import CURRENCY
from shared_utils import get_categories, update_categories_firestore

# Check authentication
check_auth()

# Initialize Firebase
if not firebase_admin._apps:
    try:
        cred = firebase_admin.credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}. Please ensure 'firebase_key.json' is correctly placed and valid.")
        st.stop()

db = firestore.client()

user_id = st.session_state.user_id

# Page config
st.set_page_config(
    page_title="Settings - WalletGenie",
    page_icon="⚙️",
    layout="wide"
)

st.title("Settings ⚙️")

# Function to get user transactions (for activity chart)
def get_user_transactions(uid):
    tx_ref = db.collection("users").document(uid).collection("transactions").stream()
    return [tx.to_dict() for tx in tx_ref]

# --- Recent Activity Section ---
st.header("Recent Transaction Activity 📊")
st.write("View your recent transaction activity.")

# Fetch recent transactions for the 24-hour activity chart
tx_data = get_user_transactions(user_id)
df = pd.DataFrame(tx_data)

if not df.empty and 'date' in df.columns and 'amount' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date', 'amount'], inplace=True)

    # Filter for transactions in the last 24 hours
    recent_transactions = df[df['date'] >= (datetime.now() - timedelta(days=1))].copy()
    if not recent_transactions.empty:
        # Extract hour of day for plotting
        recent_transactions['hour'] = recent_transactions['date'].dt.hour
        hourly_activity = recent_transactions.groupby('hour')['amount'].sum().reset_index()
        # Ensure all hours are present for a smooth chart
        all_hours = pd.DataFrame({'hour': range(24)})
        hourly_activity = pd.merge(all_hours, hourly_activity, on='hour', how='left').fillna(0)

        fig = px.bar(
            hourly_activity,
            x='hour',
            y='amount',
            title='Last 24-Hour Transaction Activity',
            labels={'hour': 'Hour of Day (24-hour format)', 'amount': f'Transaction Amount ({CURRENCY})'}
        )
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transactions recorded in the last 24 hours.")
else:
    st.info("No transaction data available to show activity.")

st.markdown("---")

# --- Config Categories Section ---
st.header("Configure Transaction Categories 📝")
st.write("Manage your custom income and expense categories. You can add up to 10 categories for each type.")

MAX_CATEGORIES = 20

# Get categories directly from Firestore (no caching)
user_categories = get_categories(db, user_id)
expense_categories = user_categories.get("expense", [])
income_categories = user_categories.get("income", [])


st.subheader("Add New Category")

with st.form("new_category_form"):
    new_category_name = st.text_input("Category Name", placeholder="e.g., Groceries, Freelance Income").strip()
    new_category_type = st.selectbox("Category Type", ["Expense", "Income"])

    add_button_disabled = False
    if new_category_type == "Expense" and len(expense_categories) >= MAX_CATEGORIES:
        add_button_disabled = True
        st.warning(f"You have reached the maximum of {MAX_CATEGORIES} expense categories.")
    elif new_category_type == "Income" and len(income_categories) >= MAX_CATEGORIES:
        add_button_disabled = True
        st.warning(f"You have reached the maximum of {MAX_CATEGORIES} income categories.")

    submit_add_category = st.form_submit_button(
        "Add Category",
        disabled=add_button_disabled
    )

    if submit_add_category:
        if new_category_name:
            if new_category_type == "Expense":
                if new_category_name not in expense_categories:
                    expense_categories.append(new_category_name)
                    update_categories_firestore(db, user_id, {"expense": expense_categories, "income": income_categories})
                    st.success(f"Category '{new_category_name}' ({new_category_type}) added successfully!")
                    st.rerun()
                else:
                    st.warning("Category already exists for Expense type.")
            else: # Income
                if new_category_name not in income_categories:
                    income_categories.append(new_category_name)
                    update_categories_firestore(db, user_id, {"expense": expense_categories, "income": income_categories})
                    st.success(f"Category '{new_category_name}' ({new_category_type}) added successfully!")
                    st.rerun()
                else:
                    st.warning("Category already exists for Income type.")
        else:
            st.error("Please enter a category name.")

st.subheader("Manage Existing Categories")

# Display deletion notification if a category was deleted
if "deleted_category" in st.session_state:
    st.success(f"Category '{st.session_state.deleted_category}' has been deleted successfully!")
    # Clear the notification after displaying it once
    del st.session_state.deleted_category

col_exp_cat, col_inc_cat = st.columns(2)

with col_exp_cat:
    st.write("**Expense Categories**")
    if expense_categories:
        for i, cat in enumerate(expense_categories):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"• {cat}")
            with col2:
                if st.button("Delete", key=f"del_exp_{i}"):
                    if "deleted_category" not in st.session_state:
                        st.session_state.deleted_category = cat
                        expense_categories.remove(cat)
                        update_categories_firestore(db, user_id, {"expense": expense_categories, "income": income_categories})
                        st.rerun()
    else:
        st.write("No custom expense categories defined yet.")

with col_inc_cat:
    st.write("**Income Categories**")
    if income_categories:
        for i, cat in enumerate(income_categories):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"• {cat}")
            with col2:
                if st.button("Delete", key=f"del_inc_{i}"):
                    if "deleted_category" not in st.session_state:
                        st.session_state.deleted_category = cat
                        income_categories.remove(cat)
                        update_categories_firestore(db, user_id, {"expense": expense_categories, "income": income_categories})
                        st.rerun()
    else:
        st.write("No custom income categories defined yet.")

# Danger Zone
st.markdown("---")
st.header("Danger Zone ⚠️")

with st.expander("Delete All Transactions"):
    st.warning("This action cannot be undone. All your transaction data will be permanently deleted.")
    
    # GitHub-style confirmation
    confirmation_text = f"delete-all-transactions-{user_id[:5]}"
    user_confirmation = st.text_input(
        f"To confirm, type '{confirmation_text}' below:",
        key="delete_confirmation"
    )
    
    if st.button("Delete All Transactions", type="primary", use_container_width=True):
        if user_confirmation == confirmation_text:
            # Use the shared utility function to delete all transactions
            from shared_utils import delete_all_transactions
            success = delete_all_transactions(db, user_id)
            
            if success:
                st.success("All transactions have been deleted successfully!")
                st.balloons()
        else:
            st.error("Confirmation text doesn't match. Transactions were not deleted.")

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))