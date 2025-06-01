from calendar import month
import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

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

# Get user's expense categories
user_categories = get_categories(db, user_id)
expense_categories = user_categories.get("expense", [])

# If no custom categories, use default ones
if not expense_categories:
    expense_categories = ["Housing", "Transportation", "Food", "Utilities", "Healthcare", "Savings", "Entertainment", "Other"]

# Get existing budget data
budget_data = get_budget(db, user_id)
monthly_income = budget_data.get("monthly_income", 5000.0)
budget_categories = budget_data.get("categories", {})

# Initialize budget categories if they don't exist
for category in expense_categories:
    if category not in budget_categories:
        budget_categories[category] = {
            "recommended": 0.10,  # Default 10% recommendation
            "current": monthly_income * 0.10,  # Default allocation
            "spent": 0.0  # Default spent amount
        }

# Calculate total spent from transactions
def calculate_spent_amounts():
    # Get transactions from the last 30 days
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%m/%d/%Y")
    
    tx_ref = db.collection("users").document(user_id).collection("transactions").stream()
    transactions = [tx.to_dict() for tx in tx_ref]
    
    # Calculate spent amount for each category
    spent_by_category = {}
    for tx in transactions:
        if tx.get("type") == "Expense":
            category = tx.get("category")
            amount = float(tx.get("amount", 0))
            
            if category in spent_by_category:
                spent_by_category[category] += amount
            else:
                spent_by_category[category] = amount
    
    # Update budget_categories with actual spent amounts
    for category, amount in spent_by_category.items():
        if category in budget_categories:
            budget_categories[category]["spent"] = amount
    
    return spent_by_category

# Calculate actual spent amounts
spent_by_category = calculate_spent_amounts()

# Budget Summary at the top
st.subheader("Budget Summary")
total_budgeted = sum(data.get("current", 0) for data in budget_categories.values())
total_spent = sum(data.get("spent", 0) for data in budget_categories.values())

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Total Budgeted",
        f"{CURRENCY} {total_budgeted:,.2f}",
        f"{(total_budgeted/monthly_income)*100:.1f}% of income" if monthly_income > 0 else "0.0% of income"
    )
with col2:
    st.metric(
        "Total Spent",
        f"{CURRENCY} {total_spent:,.2f}",
        f"{(total_spent/monthly_income)*100:.1f}% of income" if monthly_income > 0 else "0.0% of income"
    )
with col3:
    st.metric(
        "Remaining Budget",
        f"{CURRENCY} {(total_budgeted - total_spent):,.2f}",
        f"{CURRENCY} {(monthly_income - total_budgeted):,.2f} unallocated"
    )

st.markdown("---")

# Monthly income input
monthly_income = st.number_input(
    f"Monthly Income ({CURRENCY})",
    min_value=0.0,
    value=float(monthly_income) if monthly_income else 0.0,
    step=100.0,
    format="%0.2f"
)

# Display budget allocation for each category
st.subheader("Budget Allocation")

for category in expense_categories:
    with st.container():
        st.markdown(f"### {category}")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        # Get category data or initialize if it doesn't exist
        if category not in budget_categories:
            budget_categories[category] = {
                "recommended": 0.10,
                "current": monthly_income * 0.10,
                "spent": 0.0
            }
        
        category_data = budget_categories[category]
        
        with col1:
            recommended_amount = monthly_income * category_data.get("recommended", 0.10)
            current_amount = st.number_input(
                f"Budget for {category} ({CURRENCY})",
                min_value=0.0,
                value=category_data.get("current", recommended_amount),
                step=50.0,
                key=f"budget_{category}"
            )
            budget_categories[category]["current"] = current_amount
        
        with col2:
            st.markdown(f"Recommended: {CURRENCY} {recommended_amount:,.2f}")
            st.markdown(f"({category_data.get('recommended', 0.10)*100:.0f}% of income)")
        
        with col3:
            spent_amount = category_data.get("spent", 0)
            progress = spent_amount / current_amount if current_amount > 0 else 0
            st.progress(min(progress, 1.0))
            if progress > 0.9:
                st.warning("⚠️ Near budget limit!")
            st.markdown(f"Spent: {CURRENCY} {spent_amount:,.2f}")

# Save button
if st.button("Save Budget", type="primary"):
    # Update budget data in Firestore
    budget_data = {
        "monthly_income": monthly_income,
        "categories": budget_categories,
        "last_updated": datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    }
    update_budget(db, user_id, budget_data)
    st.success("Budget saved successfully!")

# Recommendations
st.subheader("Smart Recommendations 💡")
recommendations = []

if total_budgeted > monthly_income:
    recommendations.append("⚠️ Your total budget exceeds your income. Consider adjusting some categories.")
if total_budgeted < monthly_income * 0.9:
    recommendations.append("💡 You have unallocated income. Consider adding it to your savings or investment budget.")
if "Savings" in budget_categories and budget_categories["Savings"]["current"] < monthly_income * 0.1:
    recommendations.append("💰 Your savings budget is below recommended levels. Try to save at least 10% of your income.")

for rec in recommendations:
    st.markdown(f"""
        <div class="recommendation">
        {rec}
        </div>
    """, unsafe_allow_html=True)

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))