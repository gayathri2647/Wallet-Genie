import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random
from datetime import datetime, timedelta
import sys
import os
import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np # Ensure numpy is imported for potential use if needed

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from config import CURRENCY, THEME, CUSTOM_CSS # Assuming config.py exists for currency/theme

# Check authentication
check_auth()
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase_key.json") # Ensure this path is correct
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}. Please ensure 'firebase_key.json' is correctly placed and valid.")
        st.stop() # Stop the app if Firebase can't be initialized

db = firestore.client()

# --- IMPORTANT: Replace with dynamic user ID ---
user_id = "yugesh_demo_uid"
# --- End of IMPORTANT ---

# Page config
st.set_page_config(
    page_title="Dashboard - WalletGenie",
    page_icon="🧞‍♂️",
    layout="wide", # Use wide layout for more space for charts
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

# Header with greeting
st.title(f"Welcome back, {get_username()}! 👋")

################################################################################
# Get user transactions from Firestore
@st.cache_data(ttl=60) # Cache transaction data for performance
def get_user_transactions(uid):
    tx_ref = db.collection("users").document(uid).collection("transactions").stream()
    return [tx.to_dict() for tx in tx_ref]

tx_data = get_user_transactions(user_id)

# Convert to DataFrame
df = pd.DataFrame(tx_data)

# Ensure 'amount', 'type', 'date', and 'category' columns exist and are correctly typed
if not df.empty and all(col in df.columns for col in ['amount', 'type', 'date', 'category']):
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['type'] = df['type'].str.lower().str.strip()  # make sure type is lowercase for comparison
    df['category'] = df['category'].astype(str) # Ensure category is string
    df.dropna(subset=['amount', 'date', 'type', 'category'], inplace=True) # Drop rows with invalid data

    # Calculate current month and year financial summary
    now = pd.Timestamp.now()
    current_month_df = df[(df['date'].dt.month == now.month) & (df['date'].dt.year == now.year)]
    monthly_income = current_month_df[current_month_df['type'] == 'income']['amount'].sum()
    monthly_spend = current_month_df[current_month_df['type'] == 'expense']['amount'].sum()
    total_income = df[df['type'] == 'income']['amount'].sum()
    total_spend = df[df['type'] == 'expense']['amount'].sum()
    total_balance = total_income - total_spend
    df_expenses = df[df['type'] == 'expense'].copy() # Use .copy() to avoid SettingWithCopyWarning
    df_income = df[df['type'] == 'income'].copy() # Also create df for income
else:
    # Initialize variables and empty DataFrames if main DataFrame is empty or missing columns
    monthly_income = 0.0
    monthly_spend = 0.0
    total_balance = 0.0
    df_expenses = pd.DataFrame(columns=['amount', 'date', 'type', 'category'])
    df_income = pd.DataFrame(columns=['amount', 'date', 'type', 'category'])
    df = pd.DataFrame(columns=['amount', 'date', 'type', 'category']) # Ensure df is also empty but with columns

# --- Key Metrics ---
st.subheader("Current Financial Summary")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Total Balance",
        value=f"{CURRENCY} {total_balance:,.2f}",
    )
with col2:
    st.metric(
        label="Monthly Spend",
        value=f"{CURRENCY} {monthly_spend:,.2f}",
    )
with col3:
    st.metric(
        label="Monthly Income",
        value=f"{CURRENCY} {monthly_income:,.2f}",
    )

# --- Charts Section (Integrating from Reports & Charts.py) ---
st.markdown("---") # Separator for visual clarity
st.subheader("Your Financial Insights")

# 1. Monthly Spending Trend / Daily Spending Pattern
st.markdown("#### Daily Spending Trend")
if not df.empty:
    # Group by date (only date part) and sum the amounts
    daily_totals = df.groupby(df["date"].dt.date)["amount"].sum().reset_index()
    daily_totals.rename(columns={"date": "Date", "amount": "Amount"}, inplace=True)
    fig_trend = px.line(
        daily_totals,
        x="Date",
        y="Amount",
        title="Overall Daily Transaction Activity",
        labels={"Amount": f"Amount ({CURRENCY})", "Date": "Date"}
    )
    fig_trend.update_layout(hovermode="x unified") # Enhances tooltip experience
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("No transaction data to display spending trends. Add some transactions to see your patterns!")

st.markdown("---") # Separator

# 2. Category Breakdown (Bar Chart) & Category Distribution (Pie Chart) for Expenses
col_charts_expense_1, col_charts_expense_2 = st.columns(2)

with col_charts_expense_1:
    st.markdown("#### Expense Breakdown by Category")
    if not df_expenses.empty:
        category_totals = df_expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
        fig_bar_expense = px.bar(
            category_totals,
            title="Total Spending by Category",
            x=category_totals.index,
            y="amount",
            labels={"amount": f"Total Amount ({CURRENCY})", "category": "Category"},
            color=category_totals.index, # Color bars by category
            color_discrete_sequence=px.colors.qualitative.Set3 # Example color sequence
        )
        fig_bar_expense.update_layout(xaxis_title="Category", yaxis_title=f"Total Amount ({CURRENCY})")
        st.plotly_chart(fig_bar_expense, use_container_width=True)
    else:
        st.info("No expense data to display category breakdown.")

with col_charts_expense_2:
    st.markdown("#### Expense Distribution")
    if not df_expenses.empty:
        fig_pie_expense = px.pie(
            df_expenses,
            values="amount",
            names="category",
            title="Proportion of Expenses by Category",
            hole=0.3, # Creates a donut chart
            color_discrete_sequence=px.colors.qualitative.Pastel # Another example color sequence
        )
        st.plotly_chart(fig_pie_expense, use_container_width=True)
    else:
        st.info("No expense data to display category distribution.")

st.markdown("---") # Separator

# 3. Income Breakdown (Bar Chart) & Income Distribution (Pie Chart)
col_charts_income_1, col_charts_income_2 = st.columns(2)

with col_charts_income_1:
    st.markdown("#### Income Breakdown by Category")
    if not df_income.empty:
        income_category_totals = df_income.groupby("category")["amount"].sum().sort_values(ascending=False)
        fig_bar_income = px.bar(
            income_category_totals,
            title="Total Income by Category",
            x=income_category_totals.index,
            y="amount",
            labels={"amount": f"Total Amount ({CURRENCY})", "category": "Category"},
            color=income_category_totals.index,
            color_discrete_sequence=px.colors.qualitative.D3 # Another example color sequence
        )
        fig_bar_income.update_layout(xaxis_title="Category", yaxis_title=f"Total Amount ({CURRENCY})")
        st.plotly_chart(fig_bar_income, use_container_width=True)
    else:
        st.info("No income data to display category breakdown.")

with col_charts_income_2:
    st.markdown("#### Income Distribution")
    if not df_income.empty:
        fig_pie_income = px.pie(
            df_income,
            values="amount",
            names="category",
            title="Proportion of Income by Category",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Vivid # Another example color sequence
        )
        st.plotly_chart(fig_pie_income, use_container_width=True)
    else:
        st.info("No income data to display category distribution.")

# --- End of Charts Section ---


# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))