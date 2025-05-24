import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import base64
from io import BytesIO

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username

# Check authentication
check_auth()

# Page config
st.set_page_config(
    page_title="Reports & Charts - WalletGenie",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stat-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Reports & Charts 📈")

# Date range selector
col1, col2 = st.columns(2)
with col1:
    selected_month = st.selectbox(
        "Month",
        ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"],
        index=datetime.now().month - 1
    )
with col2:
    year_options = list(range(2020, datetime.now().year + 1))
    selected_year = st.selectbox(
        "Year",
        year_options,
        index=len(year_options) - 1
    )

# Generate mock data
def generate_mock_data(month, year):
    days = 30  # Simplified
    dates = [datetime(year, month, d) for d in range(1, days + 1)]
    categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment"]
    
    data = []
    for date in dates:
        for category in categories:
            amount = np.random.normal(100, 30)  # Random amounts
            data.append({
                "Date": date,
                "Category": category,
                "Amount": abs(amount)
            })
    
    return pd.DataFrame(data)

df = generate_mock_data(datetime.now().month, datetime.now().year)

# Monthly trend chart
st.subheader("Monthly Spending Trend")
daily_totals = df.groupby("Date")["Amount"].sum().reset_index()
fig_trend = px.line(
    daily_totals,
    x="Date",
    y="Amount",
    title="Daily Spending Pattern"
)
st.plotly_chart(fig_trend, use_container_width=True)

# Category breakdown
col1, col2 = st.columns(2)

with col1:
    st.subheader("Category Breakdown")
    category_totals = df.groupby("Category")["Amount"].sum()
    fig_bar = px.bar(
        category_totals,
        title="Spending by Category",
        color=category_totals.index,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("Category Distribution")
    fig_pie = px.pie(
        df,
        values="Amount",
        names="Category",
        title="Expense Distribution",
        hole=0.3
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Category-wise statistics
st.subheader("Category Statistics")
stats_cols = st.columns(3)

category_stats = df.groupby("Category").agg({
    "Amount": ["sum", "mean", "count"]
}).reset_index()
category_stats.columns = ["Category", "Total", "Average", "Transactions"]

for i, (_, row) in enumerate(category_stats.iterrows()):
    with stats_cols[i % 3]:
        st.markdown(f"""
            <div class="stat-card">
                <h3>{row['Category']}</h3>
                <p>Total: ${row['Total']:,.2f}</p>
                <p>Average: ${row['Average']:,.2f}</p>
                <p>Transactions: {int(row['Transactions'])}</p>
            </div>
        """, unsafe_allow_html=True)

# Download PDF Report
def create_download_link():
    # Mock PDF generation - in reality, you'd generate a proper PDF
    # This is just a placeholder that creates a text file
    report = f"""
    WalletGenie Financial Report
    ===========================
    Month: {selected_month} {selected_year}
    Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Total Spending: ${df['Amount'].sum():,.2f}
    Number of Transactions: {len(df)}
    
    Category Breakdown:
    {category_stats.to_string()}
    """
    
    b64 = base64.b64encode(report.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="financial_report.txt">Download Report</a>'

st.subheader("Download Report")
st.markdown(create_download_link(), unsafe_allow_html=True)

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))