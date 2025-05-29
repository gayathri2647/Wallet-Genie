import streamlit as st # type: ignore
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random
from datetime import datetime, timedelta
import sys
import os
import firebase_admin
from firebase_admin import credentials, firestore
import plotly.express as px

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from config import CURRENCY, THEME, CUSTOM_CSS

# Check authentication
check_auth()
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")  # Replace with your JSON file path
    firebase_admin.initialize_app(cred)

db = firestore.client()

user_id = st.session_state.user_id

# Page config
st.set_page_config(
    page_title="Dashboard - WalletGenie",
    page_icon="🧞‍♂️",
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

# Header with greeting
st.title(f"Welcome back, {get_username()}! 👋")


################################################################################
# Get user transactions from Firestore
def get_user_transactions(uid):
    tx_ref = db.collection("users").document(uid).collection("transactions").stream()
    return [tx.to_dict() for tx in tx_ref]

tx_data = get_user_transactions(user_id)

# Convert to DataFrame
df = pd.DataFrame(tx_data)

# Make sure 'amount', 'type', and 'date' columns exist
if not df.empty and all(col in df.columns for col in ['amount', 'type', 'date']):
    # 1. Convert types safely
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['type'] = df['type'].str.lower().str.strip()  # make sure type is lowercase for comparison
    # Drop rows with invalid dates or missing amounts/types

    # 2. Filter for current month and year
    now = pd.Timestamp.now()
    current_month_df = df[(df['date'].dt.month == now.month) & (df['date'].dt.year == now.year)]
     
    # 3. Calculate totals
    monthly_income = current_month_df[current_month_df['type'] == 'income']['amount'].sum()
    monthly_spend = current_month_df[current_month_df['type'] == 'expense']['amount'].sum()
    total_income = df[df['type'] == 'income']['amount'].sum()
    total_spend = df[df['type'] == 'expense']['amount'].sum()
    df_expenses =  df[df['type'] == 'expense']
    total_balance = total_income - total_spend
else:
    monthly_income = 0.0
    monthly_spend = 0.0
    total_balance = 0.0
################################################################################

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Total Balance",
        value=f"{CURRENCY} {total_balance:,.2f}",
        #delta=f"+{CURRENCY} 340.50"
    )
with col2:
    st.metric(
        label="Monthly Spend",
        value=f"{CURRENCY} {monthly_spend:,.2f}",
       # delta=f"-{CURRENCY} 120.25 from last month"
    )
with col3:
    st.metric(
        label="Monthly Income",
        value=f"{CURRENCY} {monthly_income:,.2f}",
       # delta="Positive cash flow"
    )

# Expense breakdown pie chart
#############################################################################################
# Group by category and sum amounts
df_expenses_grouped = df_expenses.groupby('category', as_index=False)['amount'].sum()
df_expenses_grouped.rename(columns={"category": "Category", "amount": "Amount"}, inplace=True)
###############################################################################################

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Expense Breakdown")
    fig_pie = px.pie(
        df_expenses_grouped,
        values='Amount',
        names='Category',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_pie, use_container_width=True)


###############################################################################################
# Weekly trend
df_expenses = df[df['type'] == 'expense'].copy()

# Ensure 'date' is datetime
df_expenses['date'] = pd.to_datetime(df_expenses['date'], errors='coerce')

# Filter last 7 days
today = pd.Timestamp.today().normalize()
last_week = today - pd.Timedelta(days=6)
df_week = df_expenses[(df_expenses['date'] >= last_week) & (df_expenses['date'] <= today)]

# Create 'only_date' column from datetime (date only, no time)
df_week.loc[:, 'only_date'] = df_week['date'].dt.date  # This line must be present before groupby

# Group by 'only_date' and sum amounts
df_trend = df_week.groupby('only_date', as_index=False)['amount'].sum()

# Rename columns for plotting
df_trend.rename(columns={'only_date': 'Date', 'amount': 'Spend'}, inplace=True)

# Convert 'Date' column to datetime (optional but safer for plotly)
df_trend['Date'] = pd.to_datetime(df_trend['Date'])
###########################################################################################

with col2:
    st.subheader("Weekly Trend")
    fig_line = px.line(
        df_trend,
        x='Date',
        y='Spend',
        markers=True
    )
    fig_line.update_layout(showlegend=False)
    st.plotly_chart(fig_line, use_container_width=True)

# Smart alerts
# st.subheader("Smart Alerts 🔔")
# alert_container = st.container()
# with alert_container:
#     st.markdown("""
#         <div class="warning-box">
#         ⚠️ <b>Spending Alert:</b> Your entertainment expenses are 25% higher than usual this month.<br>
#         💡 <b>Tip:</b> Consider reviewing your subscription services.
#         </div>
#     """, unsafe_allow_html=True)

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))