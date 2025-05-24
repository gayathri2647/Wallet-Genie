import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random
from datetime import datetime, timedelta
import sys
import os

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from config import CURRENCY, THEME, CUSTOM_CSS

# Check authentication
check_auth()

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

# Mock data for demonstration
total_balance = 5240.50
monthly_spend = 1850.75
monthly_income = 3500.00

# Metrics in cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Total Balance",
        value=f"{CURRENCY} {total_balance:,.2f}",
        delta=f"+{CURRENCY} 340.50"
    )
with col2:
    st.metric(
        label="Monthly Spend",
        value=f"{CURRENCY} {monthly_spend:,.2f}",
        delta=f"-{CURRENCY} 120.25 from last month"
    )
with col3:
    st.metric(
        label="Income vs Expense",
        value=f"{CURRENCY} {monthly_income - monthly_spend:,.2f}",
        delta="Positive cash flow"
    )

# Expense breakdown pie chart
expense_data = {
    'Category': ['Housing', 'Food', 'Transport', 'Entertainment', 'Utilities'],
    'Amount': [800, 400, 250, 200, 200]
}
df_expenses = pd.DataFrame(expense_data)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Expense Breakdown")
    fig_pie = px.pie(
        df_expenses,
        values='Amount',
        names='Category',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Weekly trend
dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(7, 0, -1)]
amounts = [random.uniform(50, 200) for _ in range(7)]
df_trend = pd.DataFrame({'Date': dates, 'Spend': amounts})

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
st.subheader("Smart Alerts 🔔")
alert_container = st.container()
with alert_container:
    st.markdown("""
        <div class="warning-box">
        ⚠️ <b>Spending Alert:</b> Your entertainment expenses are 25% higher than usual this month.<br>
        💡 <b>Tip:</b> Consider reviewing your subscription services.
        </div>
    """, unsafe_allow_html=True)

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))