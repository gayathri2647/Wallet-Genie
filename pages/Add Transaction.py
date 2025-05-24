import streamlit as st
import sys
import os
from datetime import datetime
import random

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username

# Check authentication
check_auth()

# Page config
st.set_page_config(
    page_title="Add Transaction - WalletGenie",
    page_icon="💰",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .prediction-card {
        background-color: #e8f4f9;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #4682b4;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Add New Transaction 💰")

# Transaction form
with st.form("transaction_form"):
    description = st.text_input("Description", placeholder="Enter transaction description")
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Amount ($)", min_value=0.01, format="%0.2f")
    with col2:
        date = st.date_input("Date", value=datetime.now())
    
    transaction_type = st.selectbox("Type", ["Expense", "Income"])
    
    submit_button = st.form_submit_button("Add Transaction")

# Handle form submission
if submit_button:
    if description and amount:
        # Mock category prediction (placeholder for TensorFlow.js integration)
        categories = ["Food & Dining", "Transportation", "Shopping", "Entertainment", "Bills & Utilities"]
        predicted_category = random.choice(categories)
        confidence = random.uniform(0.7, 0.99)
        
        # Display prediction
        st.markdown(f"""
            <div class="prediction-card">
            <h4>🤖 AI Category Prediction</h4>
            Category: <b>{predicted_category}</b><br>
            Confidence: {confidence:.1%}
            </div>
        """, unsafe_allow_html=True)
        
        # Mock API call
        st.success("Transaction added successfully!")
        
        # Show what would be sent to backend
        st.write("Transaction Details:")
        st.json({
            "description": description,
            "amount": amount,
            "date": date.strftime("%Y-%m-%d"),
            "type": transaction_type,
            "predicted_category": predicted_category,
            "user": get_username()
        })
    else:
        st.error("Please fill in all required fields.")

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))