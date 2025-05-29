import streamlit as st
import sys
import os
import firebase_admin
from firebase_admin import firestore
import time # For simulating sync delay
import pandas as pd
import plotly.express as px # For the 24-hour activity chart
from datetime import datetime, timedelta # <--- ADD THIS LINE

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from firebase_init import init_firestore # Assuming firebase_init.py exists in the root
from config import CURRENCY # Assuming CURRENCY is defined in config.py

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

# --- IMPORTANT: Replace with dynamic user ID ---
# In a real application, get the actual user ID from your authentication system
user_id = "yugesh_demo_uid"
# --- End of IMPORTANT ---

# Page config
st.set_page_config(
    page_title="Settings - WalletGenie",
    page_icon="⚙️",
    layout="wide"
)

st.title("Settings ⚙️")

# --- Function to fetch categories (Moved here for consolidation) ---
@st.cache_data(ttl=60)
def get_categories(uid):
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("categories", {"expense": [], "income": []})
    return {"expense": [], "income": []}

# Function to update categories in Firestore (Moved here for consolidation)
def update_categories_firestore(uid, categories_data):
    doc_ref = db.collection("users").document(uid)
    doc_ref.set({"categories": categories_data}, merge=True)

# Function to get user transactions (Needed for Smart Sync chart)
@st.cache_data(ttl=60)
def get_user_transactions(uid):
    tx_ref = db.collection("users").document(uid).collection("transactions").stream()
    return [tx.to_dict() for tx in tx_ref]

# --- Smart Sync Section ---
st.header("Smart Sync Settings 🔄")
st.write("Manage your automatic transaction synchronization and view recent activity.")

# Current sync status (example, could be fetched from user settings in Firestore)
sync_enabled_key = f"sync_enabled_{user_id}"
if sync_enabled_key not in st.session_state:
    st.session_state[sync_enabled_key] = True # Default to enabled

sync_enabled = st.session_state[sync_enabled_key]

# Display current sync status
if sync_enabled:
    st.success("✅ Smart Sync is currently enabled. Your transactions are automatically syncing.")
else:
    st.warning("⚠️ Smart Sync is currently disabled. Enable it below to get real-time updates.")

# Toggle for Smart Sync
if st.checkbox("Enable Smart Sync", value=sync_enabled, key="toggle_sync"):
    st.session_state[sync_enabled_key] = True
    st.toast("Smart Sync Enabled!")
else:
    st.session_state[sync_enabled_key] = False
    st.toast("Smart Sync Disabled!")

if sync_enabled:
    st.subheader("Recent Sync Activity")
    # Fetch recent transactions for the 24-hour activity chart
    tx_data = get_user_transactions(user_id)
    df = pd.DataFrame(tx_data)

    if not df.empty and 'date' in df.columns and 'amount' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date', 'amount'], inplace=True) # Drop rows with invalid dates/amounts

        # Filter for transactions in the last 24 hours (approx)
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
            fig.update_layout(xaxis=dict(tickmode='linear', dtick=1)) # Show all hours
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No transactions recorded in the last 24 hours.")
    else:
        st.info("No transaction data available to show sync activity.")

    st.subheader("Sync Settings")
    col1_sync, col2_sync = st.columns(2)

    with col1_sync:
        st.selectbox(
            "Sync Frequency",
            ["Every 15 minutes", "Every 30 minutes", "Every hour", "Every 4 hours", "Daily"],
            key="sync_frequency_setting"
        )
        st.checkbox("Notify on sync failure", value=True, key="notify_sync_failure")

    with col2_sync:
        st.multiselect(
            "Sync Categories",
            ["Transactions", "Account Balance", "Bills", "Investments"],
            default=["Transactions", "Account Balance"],
            key="sync_data_categories"
        )
        st.checkbox("Auto-categorize new transactions", value=True, key="auto_categorize")

else:
    st.warning("""
        ⚠️ Smart Sync is disabled. Enable it to:
        - Automatically sync your transactions
        - Get real-time balance updates
        - Receive smart notifications
        - Keep your data up-to-date across devices
    """)

# Manual sync button
if st.button("Sync Now", disabled=not sync_enabled):
    with st.spinner("Syncing your data..."):
        time.sleep(2) # Simulate sync delay
        st.success("Data synced successfully!")
        st.rerun() # Rerun to refresh status and charts if needed

st.markdown("---") # Separator

# --- Config Categories Section ---
st.header("Configure Transaction Categories 📝")
st.write("Manage your custom income and expense categories. You can add up to 10 categories for each type.")

MAX_CATEGORIES = 10 # Maximum number of categories allowed for each type (expense/income)

user_categories = get_categories(user_id)
expense_categories = user_categories.get("expense", [])
income_categories = user_categories.get("income", [])

col_exp_cat, col_inc_cat = st.columns(2)

with col_exp_cat:
    st.subheader("Existing Expense Categories")
    if expense_categories:
        for cat in expense_categories:
            st.info(f"• {cat}")
    else:
        st.info("No custom expense categories defined yet.")

with col_inc_cat:
    st.subheader("Existing Income Categories")
    if income_categories:
        for cat in income_categories:
            st.info(f"• {cat}")
    else:
        st.info("No custom income categories defined yet.")

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
                    update_categories_firestore(user_id, {"expense": expense_categories, "income": income_categories})
                    st.success(f"Category '{new_category_name}' ({new_category_type}) added successfully!")
                    st.rerun()
                else:
                    st.warning("Category already exists for Expense type.")
            else: # Income
                if new_category_name not in income_categories:
                    income_categories.append(new_category_name)
                    update_categories_firestore(user_id, {"expense": expense_categories, "income": income_categories})
                    st.success(f"Category '{new_category_name}' ({new_category_type}) added successfully!")
                    st.rerun()
                else:
                    st.warning("Category already exists for Income type.")
        else:
            st.error("Please enter a category name.")

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))