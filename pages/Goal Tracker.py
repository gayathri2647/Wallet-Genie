import streamlit as st
import plotly.express as px
import pandas as pd
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
    page_title="Goal Tracker - WalletGenie",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .goal-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .on-track {
        border-left: 5px solid #90EE90;
    }
    .off-track {
        border-left: 5px solid #FFB6C1;
    }
    .goal-form {
        background-color: #e8f4f9;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Goal Tracker 🎯")
st.write("Track and achieve your financial goals")

# Add new goal form
st.subheader("Add New Goal")
with st.form("new_goal", clear_on_submit=True):
    st.markdown('<div class="goal-form">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        goal_name = st.text_input("Goal Name")
        goal_amount = st.number_input("Target Amount ($)", min_value=0.0, step=100.0)
    
    with col2:
        goal_deadline = st.date_input("Target Date", min_value=datetime.now().date())
        goal_category = st.selectbox(
            "Category",
            ["Savings", "Investment", "Purchase", "Debt Repayment", "Emergency Fund"]
        )
    
    submit_goal = st.form_submit_button("Add Goal")
    st.markdown('</div>', unsafe_allow_html=True)

if submit_goal and goal_name and goal_amount > 0:
    st.success(f"Goal '{goal_name}' added successfully!")

# Mock existing goals
goals = [
    {
        "name": "Emergency Fund",
        "target": 10000,
        "current": 7500,
        "deadline": datetime.now().date() + timedelta(days=90),
        "category": "Savings",
        "on_track": True
    },
    {
        "name": "New Car Down Payment",
        "target": 5000,
        "current": 2000,
        "deadline": datetime.now().date() + timedelta(days=60),
        "category": "Purchase",
        "on_track": False
    },
    {
        "name": "Vacation Fund",
        "target": 3000,
        "current": 2800,
        "deadline": datetime.now().date() + timedelta(days=30),
        "category": "Savings",
        "on_track": True
    }
]

# Display goals
st.subheader("Your Goals")

for goal in goals:
    progress = goal["current"] / goal["target"]
    status_class = "on-track" if goal["on_track"] else "off-track"
    days_left = (goal["deadline"] - datetime.now().date()).days
    
    st.markdown(f"""
        <div class="goal-card {status_class}">
            <h3>{goal["name"]}</h3>
            <p>Category: {goal["category"]}</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.progress(progress)
        st.write(f"${goal['current']:,.2f} of ${goal['target']:,.2f}")
    
    with col2:
        st.metric(
            "Days Left",
            days_left,
            f"{days_left} days"
        )
    
    with col3:
        if not goal["on_track"]:
            st.warning("⚠️ Off Track")
            required_daily = (goal["target"] - goal["current"]) / days_left
            st.write(f"Need ${required_daily:.2f}/day")
        else:
            st.success("✅ On Track")

# Goal analytics
st.subheader("Goal Analytics")

# Progress over time chart
dates = pd.date_range(start='2023-01-01', end=datetime.now(), freq='W')
progress_data = []

for goal in goals:
    for date in dates:
        # Simulate historical progress
        progress_data.append({
            "Date": date,
            "Goal": goal["name"],
            "Amount": min(goal["current"] * (1 - (datetime.now() - date.to_pydatetime()).days / 180), goal["target"])
        })

df_progress = pd.DataFrame(progress_data)

fig = px.line(
    df_progress,
    x="Date",
    y="Amount",
    color="Goal",
    title="Goal Progress Over Time"
)
st.plotly_chart(fig, use_container_width=True)

# Goal summary
col1, col2, col3 = st.columns(3)

with col1:
    total_goals = len(goals)
    on_track_goals = sum(1 for g in goals if g["on_track"])
    st.metric("Total Goals", total_goals, f"{on_track_goals} on track")

with col2:
    total_target = sum(g["target"] for g in goals)
    total_current = sum(g["current"] for g in goals)
    st.metric("Total Progress", f"${total_current:,.2f}", f"{(total_current/total_target)*100:.1f}%")

with col3:
    avg_progress = sum(g["current"]/g["target"] for g in goals) / len(goals)
    st.metric("Average Progress", f"{avg_progress*100:.1f}%")

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))