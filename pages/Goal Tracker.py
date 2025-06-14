import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import firebase_admin
from firebase_admin import firestore
import uuid

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from shared_utils import get_goals, add_goal, update_goal, delete_goal

# Check authentication
check_auth()

# Initialize Firebase
if not firebase_admin._apps:
    try:
        cred = firebase_admin.credentials.Certificate({
            "type": st.secrets["firebase_service_account"]["type"],
            "project_id": st.secrets["firebase_service_account"]["project_id"],
            "private_key_id": st.secrets["firebase_service_account"]["private_key_id"],
            "private_key": st.secrets["firebase_service_account"]["private_key"],
            "client_email": st.secrets["firebase_service_account"]["client_email"],
            "client_id": st.secrets["firebase_service_account"]["client_id"],
            "auth_uri": st.secrets["firebase_service_account"]["auth_uri"],
            "token_uri": st.secrets["firebase_service_account"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["firebase_service_account"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["firebase_service_account"]["client_x509_cert_url"],
            "universe_domain": st.secrets["firebase_service_account"]["universe_domain"]
        })
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}. Please ensure '.streamlit/secrets.toml' is correctly configured.")
        st.stop()

db = firestore.client()
user_id = st.session_state.user_id

# Page config
st.set_page_config(
    page_title="Goal Tracker - WalletGenie",
    page_icon="🎯",
    layout="centered"  # Changed to wide layout for better spacing
)

# Custom CSS
st.markdown("""
    <style>
    .goal-card {
        background-color: #262730;
        padding: 5px;
        padding-left: 10px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .on-track {
        border-left: 5px solid #00CC66;
    }
    .off-track {
        border-left: 5px solid #FF4B4B;
    }
    .goal-form {
        background-color: #1E1E1E;
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
        border: 1px solid #333;
    }
    .goal-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 10px;
        color: #FFFFFF;
    }
    .goal-category {
        font-size: 0.9rem;
        color: #9E9E9E;
        margin-bottom: 15px;
    }
    .goal-progress {
        margin: 15px 0;
    }
    .goal-metric {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    .goal-update {
        background-color: #2E2E2E;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    div.row-widget.stRadio > div {
        flex-direction: row;
        align-items: center;
    }
    div.row-widget.stRadio > div > label {
        background-color: #2E2E2E;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 5px;
        cursor: pointer;
    }
    .status-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-on-track {
        background-color: rgba(0, 204, 102, 0.2);
        color: #00CC66;
    }
    .status-off-track {
        background-color: rgba(255, 75, 75, 0.2);
        color: #FF4B4B;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar configuration
# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))

# Main content
st.title("Goal Tracker 🎯")
st.write("Track and achieve your financial goals")

# Add new goal form in a container for better styling
with st.container():
    st.subheader("Add New Goal")
    with st.form("new_goal", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            goal_name = st.text_input("Goal Name")
            goal_amount = st.number_input("Target Amount (₹)", min_value=0.0, step=100.0)
            current_amount = st.number_input("Current Amount (₹)", min_value=0.0, step=100.0)
        
        with col2:
            goal_deadline = st.date_input("Target Date", min_value=datetime.now().date())
            goal_category = st.selectbox(
                "Category",
                ["Savings", "Investment", "Purchase", "Debt Repayment", "Emergency Fund"]
            )
        
        col3, col4 = st.columns([3, 1])
        with col4:
            submit_goal = st.form_submit_button("Add Goal", type="primary", use_container_width=True)

if submit_goal and goal_name and goal_amount > 0:
    # Calculate if goal is on track
    days_left = (goal_deadline - datetime.now().date()).days
    if days_left <= 0:
        on_track = current_amount >= goal_amount
    else:
        daily_required = (goal_amount - current_amount) / days_left
        on_track = daily_required <= 0 or current_amount >= goal_amount
    
    # Create goal data
    goal_data = {
        "name": goal_name,
        "target": goal_amount,
        "current": current_amount,
        "deadline": goal_deadline.isoformat(),
        "category": goal_category,
        "on_track": on_track,
        "created_at": datetime.now().isoformat()
    }
    
    # Add goal to Firestore
    add_goal(db, user_id, goal_data)
    st.success(f"Goal '{goal_name}' added successfully!")
    st.rerun()

# Get user goals from Firestore
user_goals = get_goals(db, user_id)

# Display goals
st.markdown("---")
st.subheader("Your Goals")

if not user_goals:
    st.info("You don't have any goals yet. Add your first goal above!")
else:
    # Sort goals by deadline (closest first)
    for i, goal in enumerate(user_goals):
        # Convert deadline string back to date
        goal["deadline"] = datetime.fromisoformat(goal["deadline"]).date()
    
    user_goals.sort(key=lambda x: x["deadline"])
    
    for goal in user_goals:
        # Calculate progress
        progress = goal["current"] / goal["target"] if goal["target"] > 0 else 0
        status_class = "on-track" if goal["on_track"] else "off-track"
        days_left = (goal["deadline"] - datetime.now().date()).days
        
        # Goal card with improved layout
        with st.container():
            st.markdown(f"""
                <div class="goal-card {status_class}">
                    <div class="goal-title">{goal["name"]}</div>
                    <div class="goal-category">📊 {goal["category"]}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Create columns for better organization
            col1, col2, col3 = st.columns([2, 0.8, 1.2])
            
            with col1:
                st.markdown("### Progress")
                st.progress(min(progress, 1.0))
                st.write(f"₹{goal['current']:,.2f} of ₹{goal['target']:,.2f}")
            
            with col2:
                st.metric(
                    "Time Remaining",
                    f"{max(0, days_left)} days",
                    delta=None,
                    delta_color="normal"
                )
                
                # Status badge with improved styling
                if not goal["on_track"] and days_left > 0:
                    st.markdown(
                        f'<div class="status-badge status-off-track">⚠️ Off Track</div>',
                        unsafe_allow_html=True
                    )
                    required_daily = (goal["target"] - goal["current"]) / days_left if days_left > 0 else 0
                    st.write(f"Need ₹{required_daily:,.2f}/day")
                else:
                    status = "✅ On Track" if days_left > 0 else "✅ Complete" if goal["current"] >= goal["target"] else "❌ Incomplete"
                    st.markdown(
                        f'<div class="status-badge status-on-track">{status}</div>',
                        unsafe_allow_html=True
                    )
            
            with col3:
                # Update goal form
                update_col, delete_col = st.columns([2, 1])
                
                with update_col:
                    with st.form(key=f"update_goal_{goal['id']}"):
                        # Store original value for comparison
                        original_amount = float(goal["current"])
                        
                        new_current = st.number_input(
                            "Update Amount (₹)", 
                            min_value=0.0, 
                            value=original_amount, 
                            step=50.0
                        )
                        
                        update_submitted = st.form_submit_button(
                            "Update",
                            type="primary",
                            use_container_width=True
                        )
                        
                        if update_submitted:
                            # Calculate progress increment
                            progress_increment = new_current - original_amount
                            new_current += original_amount
                            # Recalculate if on track
                            days_left = (goal["deadline"] - datetime.now().date()).days
                            if days_left <= 0:
                                on_track = new_current >= goal["target"]
                            else:
                                daily_required = (goal["target"] - new_current) / days_left
                                on_track = daily_required <= 0 or new_current >= goal["target"]
                            
                            # Update goal in Firestore
                            update_goal(db, user_id, goal["id"], {
                                "current": new_current,
                                "on_track": on_track
                            })
                            
                            # Show appropriate message based on whether progress was added or reduced
                            if progress_increment > 0:
                                st.success(f"Goal updated! Added ₹{progress_increment:,.2f} to your progress.")
                            elif progress_increment < 0:
                                st.warning(f"Goal updated! Reduced progress by ₹{abs(progress_increment):,.2f}.")
                            else:
                                st.info("Goal updated! Progress amount unchanged.")
                                
                            st.rerun()
                
                with delete_col:
                    # Use a unique key for each delete button
                    st.markdown("Delete")
                    if st.button("🗑️", key=f"delete_goal_{goal['id']}", use_container_width=True):
                        delete_goal(db, user_id, goal["id"])
                        st.success("Goal deleted!")
                        st.rerun()

    # Goal analytics with improved layout
    if len(user_goals) > 0:
        st.markdown("---")
        st.subheader("Goal Analytics")
        
        # Progress over time chart
        progress_data = []
        for goal in user_goals:
            progress_data.append({
                "Goal": goal["name"],
                "Current": goal["current"],
                "Target": goal["target"],
                "Deadline": goal["deadline"]
            })
        
        df_progress = pd.DataFrame(progress_data)
        
        if not df_progress.empty:
            # Create a more informative chart
            fig = px.bar(
                df_progress,
                x="Goal",
                y=["Current", "Target"],
                title="Current Goal Progress",
                barmode="group",
                template="plotly_dark",
                color_discrete_sequence=["#00CC66", "#4A4A4A"],
                hover_data=["Deadline"]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Goal summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_goals = len(user_goals)
            on_track_goals = sum(1 for g in user_goals if g["on_track"])
            st.metric(
                "Total Goals",
                total_goals,
                f"{on_track_goals} on track",
                delta_color="normal"
            )
        
        with col2:
            total_target = sum(g["target"] for g in user_goals)
            total_current = sum(g["current"] for g in user_goals)
            st.metric(
                "Total Progress",
                f"₹{total_current:,.2f}",
                f"{(total_current/total_target)*100:.1f}%" if total_target > 0 else "0%",
                delta_color="normal"
            )
        
        with col3:
            # Calculate average progress correctly
            progress_percentages = [g["current"]/g["target"] for g in user_goals if g["target"] > 0]
            avg_progress = sum(progress_percentages) / len(progress_percentages) if progress_percentages else 0
            st.metric(
                "Average Progress",
                f"{avg_progress*100:.1f}%",
                delta=None,
                delta_color="normal"
            )