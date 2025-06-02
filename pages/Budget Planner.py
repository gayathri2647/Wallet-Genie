import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import firestore

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from firebase_init import init_firestore
from config import CURRENCY, THEME, CUSTOM_CSS
from shared_utils import get_categories, get_budget, update_budget

# Check authentication
check_auth()

# Initialize Firebase
db = init_firestore()
user_id = st.session_state.user_id

# Page config
st.set_page_config(
    page_title="Budget Planner - WalletGenie",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply theme
for key, value in THEME.items():
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{ {key}: {value} }}
        </style>
    """, unsafe_allow_html=True)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("Budget Planner 📊")

# Add a "Refresh Data" button
if st.button("Refresh Budget Data 🔄", key="refresh_budget_data_button"):
    # Clear the cache for the get_current_month_expenses function
    st.cache_data.clear()
    st.rerun() # Rerun the app to fetch fresh data

# Get user's expense categories
user_categories_from_firestore = get_categories(db, user_id)
expense_categories_list = user_categories_from_firestore.get("expense", [])
# Default categories if none from Firestore
default_expense_categories = ["Housing", "Food & Dining", "Transportation", "Shopping", "Entertainment", "Bills & Utilities", "Education", "Health", "Personal Care", "Others", "Savings"]
if not expense_categories_list:
    expense_categories_list = default_expense_categories


# Fetch existing budget data
existing_budget_data = get_budget(db, user_id)
if existing_budget_data and "monthly_income" in existing_budget_data:
    initial_monthly_income = float(existing_budget_data["monthly_income"]) # Explicitly cast to float
else:
    initial_monthly_income = 0.0

monthly_income = st.number_input(
    f"Monthly Income ({CURRENCY})",
    min_value=0.0,
    value=initial_monthly_income,
    step=100.0,
    format="%0.2f",
    key="monthly_income_input"
)

# Initialize budget categories (either from saved data or defaults)
if existing_budget_data and "categories" in existing_budget_data:
    budget_categories = existing_budget_data["categories"]
    # Ensure all current expense_categories_list are in budget_categories with defaults if new
    for cat in expense_categories_list:
        if cat not in budget_categories:
            budget_categories[cat] = {"recommended": 0, "current": 0, "budget": 0, "spent": 0}
else:
    # Initialize with default structure based on current expense categories list
    budget_categories = {}
    for cat in expense_categories_list:
        budget_categories[cat] = {"recommended": 0, "current": 0, "budget": 0, "spent": 0}

    if not existing_budget_data:
        default_initial_budgets = {
            "Housing": monthly_income * 0.3,
            "Food & Dining": monthly_income * 0.15,
            "Transportation": monthly_income * 0.1,
            "Shopping": monthly_income * 0.1,
            "Entertainment": monthly_income * 0.05,
            "Bills & Utilities": monthly_income * 0.1,
            "Education": monthly_income * 0.05,
            "Health": monthly_income * 0.05,
            "Personal Care": monthly_income * 0.05,
            "Others": monthly_income * 0.05,
            "Savings": monthly_income * 0.1
        }
        for cat, default_val in default_initial_budgets.items():
            if cat in budget_categories:
                budget_categories[cat]["current"] = default_val
                budget_categories[cat]["budget"] = default_val
                if "recommended" in budget_categories[cat]:
                    budget_categories[cat]["recommended"] = default_val / monthly_income if monthly_income > 0 else 0


st.subheader("Budget Categories")

# --- Fetch current month's transactions for 'spent' calculation ---
@st.cache_data(ttl=60) # Keep cache to avoid excessive Firestore reads on normal interactions
def get_current_month_expenses(uid):
    transactions_ref = db.collection("users").document(uid).collection("transactions")
    current_month = datetime.now().month
    current_year = datetime.now().year

    all_tx_docs = [doc.to_dict() for doc in transactions_ref.stream()]
    df_all_tx = pd.DataFrame(all_tx_docs)

    if not df_all_tx.empty and 'date' in df_all_tx.columns:
        df_all_tx['date'] = pd.to_datetime(df_all_tx['date'], errors='coerce')
        df_all_tx = df_all_tx.dropna(subset=['date', 'amount', 'type', 'category'])
        df_current_month = df_all_tx[
            (df_all_tx['date'].dt.month == current_month) &
            (df_all_tx['date'].dt.year == current_year) &
            (df_all_tx['type'].str.lower() == 'expense')
        ].copy()
        df_current_month['amount'] = pd.to_numeric(df_current_month['amount'], errors='coerce')
        return df_current_month
    return pd.DataFrame()

current_month_expenses_df = get_current_month_expenses(user_id)
actual_spent_by_category = {}
if not current_month_expenses_df.empty:
    actual_spent_by_category = current_month_expenses_df.groupby('category')['amount'].sum().to_dict()

# Update 'spent' values in budget_categories
for category_name, data in budget_categories.items():
    budget_categories[category_name]["spent"] = actual_spent_by_category.get(category_name, 0.0)

# Display categories and allow user to adjust
for category_name in expense_categories_list:
    if category_name in budget_categories:
        col1, col2, col3, col4 = st.columns([0.2, 0.3, 0.3, 0.2])
        with col1:
            st.markdown(f"**{category_name}**")
        with col2:
            budget_categories[category_name]["current"] = st.number_input(
                f"Budget for {category_name}",
                min_value=0.0,
                value=float(budget_categories[category_name].get("current", 0.0)),
                step=10.0,
                format="%0.2f",
                key=f"budget_{category_name}"
            )
            budget_categories[category_name]["budget"] = budget_categories[category_name]["current"]

        with col3:
            spent_amount = budget_categories[category_name].get("spent", 0.0)
            st.markdown(f"Spent: {CURRENCY} {spent_amount:,.2f}")

            budget_limit = budget_categories[category_name].get("budget", 0.0)
            if budget_limit > 0:
                progress = min(spent_amount / budget_limit, 1.0)
                st.progress(progress)
                if progress > 0.9:
                    st.warning("⚠️ Near budget limit!")
                elif progress >= 1.0:
                    st.error("❌ Budget exceeded!")
            else:
                st.progress(0.0)
                if spent_amount > 0:
                    st.info("No budget set, but spending detected.")

# Calculate totals
total_budgeted = sum(data.get("budget", 0) for data in budget_categories.values())
total_spent = sum(data.get("spent", 0) for data in budget_categories.values())

st.subheader("Budget Summary")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Total Budgeted",
        f"{CURRENCY} {total_budgeted:,.2f}",
        f"{(total_budgeted/monthly_income)*100:.1f}% of income" if monthly_income > 0 else "N/A"
    )
with col2:
    st.metric(
        "Total Spent",
        f"{CURRENCY} {total_spent:,.2f}",
        f"{(total_spent/monthly_income)*100:.1f}% of income" if monthly_income > 0 else "N/A"
    )
with col3:
    remaining_budget = total_budgeted - total_spent
    unallocated_income = monthly_income - total_budgeted
    st.metric(
        "Remaining Budget",
        f"{CURRENCY} {remaining_budget:,.2f}",
        f"{CURRENCY} {unallocated_income:,.2f} unallocated"
    )

# Save button
if st.button("Save Budget", type="primary"):
    budget_data = {
        "monthly_income": monthly_income,
        "categories": budget_categories,
        "last_updated": datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    }
    update_budget(db, user_id, budget_data)
    st.success("Budget saved successfully!")

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))