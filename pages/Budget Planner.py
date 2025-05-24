import streamlit as st
import sys
import os
import pandas as pd

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from config import CURRENCY, THEME, CUSTOM_CSS

# Check authentication
check_auth()

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

# Mock income input
monthly_income = st.number_input(
    f"Monthly Income ({CURRENCY})",
    min_value=0.0,
    value=5000.0,
    step=100.0,
    format="%0.2f"
)

# Budget categories with recommended percentages
budget_categories = {
    "Housing": {"recommended": 0.30, "current": 0.0, "spent": 0.25},
    "Transportation": {"recommended": 0.15, "current": 0.0, "spent": 0.12},
    "Food": {"recommended": 0.15, "current": 0.0, "spent": 0.14},
    "Utilities": {"recommended": 0.10, "current": 0.0, "spent": 0.08},
    "Healthcare": {"recommended": 0.10, "current": 0.0, "spent": 0.05},
    "Savings": {"recommended": 0.10, "current": 0.0, "spent": 0.15},
    "Entertainment": {"recommended": 0.05, "current": 0.0, "spent": 0.07},
    "Other": {"recommended": 0.05, "current": 0.0, "spent": 0.04}
}

# Display recommended ranges and input fields
st.subheader("Budget Allocation")

for category, data in budget_categories.items():
    with st.container():
        st.markdown(f"### {category}")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            recommended_amount = monthly_income * data["recommended"]
            current_amount = st.number_input(
                f"Budget for {category} ({CURRENCY})",
                min_value=0.0,
                value=recommended_amount,
                step=50.0,
                key=f"budget_{category}"
            )
            budget_categories[category]["current"] = current_amount
        
        with col2:
            st.markdown(f"Recommended: {CURRENCY} {recommended_amount:,.2f}")
            st.markdown(f"({data['recommended']*100:.0f}% of income)")
        
        with col3:
            spent_amount = monthly_income * data["spent"]
            progress = spent_amount / current_amount if current_amount > 0 else 0
            st.progress(min(progress, 1.0))
            if progress > 0.9:
                st.warning("⚠️ Near budget limit!")
            st.markdown(f"Spent: {CURRENCY} {spent_amount:,.2f}")

# Summary
st.subheader("Budget Summary")
total_budgeted = sum(data["current"] for data in budget_categories.values())
total_spent = sum(data["spent"] * monthly_income for data in budget_categories.values())

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Total Budgeted",
        f"{CURRENCY} {total_budgeted:,.2f}",
        f"{(total_budgeted/monthly_income)*100:.1f}% of income"
    )
with col2:
    st.metric(
        "Total Spent",
        f"{CURRENCY} {total_spent:,.2f}",
        f"{(total_spent/monthly_income)*100:.1f}% of income"
    )
with col3:
    st.metric(
        "Remaining Budget",
        f"{CURRENCY} {(total_budgeted - total_spent):,.2f}",
        f"{CURRENCY} {(monthly_income - total_budgeted):,.2f} unallocated"
    )

# Recommendations
st.subheader("Smart Recommendations 💡")
recommendations = []

if total_budgeted > monthly_income:
    recommendations.append("⚠️ Your total budget exceeds your income. Consider adjusting some categories.")
if total_budgeted < monthly_income * 0.9:
    recommendations.append("💡 You have unallocated income. Consider adding it to your savings or investment budget.")
if budget_categories["Savings"]["current"] < monthly_income * 0.1:
    recommendations.append("💰 Your savings budget is below recommended levels. Try to save at least 10% of your income.")

for rec in recommendations:
    st.markdown(f"""
        <div class="recommendation">
        {rec}
        </div>
    """, unsafe_allow_html=True)

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))