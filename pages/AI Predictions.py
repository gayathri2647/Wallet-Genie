import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username

# Check authentication
check_auth()

# Page config
st.set_page_config(
    page_title="AI Predictions - WalletGenie",
    page_icon="🔮",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .risk-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    .risk-safe {
        background-color: #90EE90;
    }
    .risk-medium {
        background-color: #FFD700;
    }
    .risk-high {
        background-color: #FFB6C1;
    }
    </style>
""", unsafe_allow_html=True)

st.title("AI Predictions 🔮")
st.write("Let's peek into your financial future!")

# Forecast duration toggle
duration = st.radio(
    "Forecast Duration",
    ["7 Days", "30 Days"],
    horizontal=True
)

# Generate mock forecast data
days = 30 if duration == "30 Days" else 7
dates = [(datetime.now() + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(days)]
base_spend = 100
trend = np.linspace(0, 0.3, days)  # Increasing trend
noise = np.random.normal(0, 0.1, days)  # Random variations
forecast = [base_spend * (1 + t + n) for t, n in zip(trend, noise)]

# Create forecast DataFrame
df_forecast = pd.DataFrame({
    'Date': dates,
    'Predicted Spend': forecast
})

# Display forecast chart
st.subheader(f"{days}-Day Spend Forecast")
fig = px.line(
    df_forecast,
    x='Date',
    y='Predicted Spend',
    markers=True
)
fig.add_scatter(
    x=df_forecast['Date'],
    y=[base_spend] * len(df_forecast),
    name='Baseline',
    line=dict(dash='dash')
)
st.plotly_chart(fig, use_container_width=True)

# Calculate risk level
total_predicted = sum(forecast)
baseline_total = base_spend * days
percent_increase = (total_predicted - baseline_total) / baseline_total * 100

# Determine risk level
if percent_increase <= 10:
    risk_level = "Safe"
    risk_class = "risk-safe"
elif percent_increase <= 25:
    risk_level = "Medium"
    risk_class = "risk-medium"
else:
    risk_level = "High"
    risk_class = "risk-high"

# Display risk level
st.subheader("Risk Assessment")
st.markdown(f"""
    <div class="risk-card {risk_class}">
        <h2>{risk_level}</h2>
        <p>Predicted spending is {percent_increase:.1f}% {
        'above' if percent_increase > 0 else 'below'} baseline</p>
    </div>
""", unsafe_allow_html=True)

# Key insights
st.subheader("Key Insights")
col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    📊 Forecast Summary:
    - Average daily spend: ${np.mean(forecast):.2f}
    - Peak spend day: ${max(forecast):.2f}
    - Total forecast: ${sum(forecast):.2f}
    """)

with col2:
    st.info(f"""
    💡 Recommendations:
    - {'Consider reducing discretionary spending' if percent_increase > 20 else 'Spending pattern looks healthy'}
    - {'Set up spending alerts' if risk_level == 'High' else 'Continue monitoring trends'}
    """)

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))