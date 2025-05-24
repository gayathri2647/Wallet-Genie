import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import pyrebase
import json
from datetime import datetime
import os
import sys

# Add the current directory to the path so that the pages can import from the root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Firebase Admin SDK (for backend operations)
try:
    cred = credentials.Certificate("firebase_key.json")   #firebase_key = wallet-3f13a-d7fbf39fbb1b
    firebase_admin.initialize_app(cred)
except ValueError:
    # App already initialized
    pass

# Configure Pyrebase (for authentication operations)
with open("firebase_config.json") as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config)
auth_pb = firebase.auth()

# Page configuration
st.set_page_config(page_title="Wallet Genie - Login", page_icon="🔐", layout="centered")

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None

def login_signup_ui():
    """Main UI function for login and signup"""
    
    # If already logged in, redirect to dashboard
    if st.session_state.logged_in:
        display_logged_in_ui()
        return
    
    # App title and description
    st.title("Wallet Genie 🧞‍♂️")
    st.markdown("Your personal finance assistant")
    
    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    # Login Tab
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_btn = st.button("Login", use_container_width=True)
        with col2:
            forgot_btn = st.button("Forgot Password?", use_container_width=True)
            
        if login_btn:
            if email and password:
                login_user(email, password)
            else:
                st.error("Please enter both email and password")
                
        if forgot_btn:
            if email:
                try:
                    auth_pb.send_password_reset_email(email)
                    st.success(f"Password reset link sent to {email}")
                except Exception as e:
                    st.error(f"Error sending reset email: {e}")
            else:
                st.warning("Please enter your email address")
    
    # Signup Tab
    with tab2:
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        signup_btn = st.button("Create Account", use_container_width=True)
        
        if signup_btn:
            if new_email and new_password and confirm_password:
                if new_password == confirm_password:
                    signup_user(new_email, new_password)
                else:
                    st.error("Passwords do not match")
            else:
                st.error("Please fill in all fields")

def login_user(email, password):
    """Handle user login"""
    try:
        user = auth_pb.sign_in_with_email_and_password(email, password)
        st.session_state.user_info = user
        st.session_state.logged_in = True
        st.session_state.authentication_status = True
        st.session_state.email = email
        
        st.success("Login successful!")
        st.balloons()
        
        # Redirect to the dashboard page
        st.switch_page("pages/2_Dashboard.py")
    except Exception as e:
        st.error(f"Login failed: {e}")
        st.session_state.authentication_status = False

def signup_user(email, password):
    """Handle user signup"""
    try:
        # Create user with Firebase Authentication
        user = auth_pb.create_user_with_email_and_password(email, password)
        
        # Send email verification
        auth_pb.send_email_verification(user['idToken'])
        
        st.success("Account created successfully! Please verify your email.")
        
        # Automatically log in the new user
        st.session_state.user_info = user
        st.session_state.logged_in = True
        st.session_state.authentication_status = True
        st.session_state.email = email
        
        # Redirect to the dashboard page
        st.switch_page("pages/Dashboard.py")
    except Exception as e:
        st.error(f"Signup failed: {e}")
        st.session_state.authentication_status = False

def display_logged_in_ui():
    """Display UI for logged in users"""
    st.title(f"Welcome to Wallet Genie! 🧞‍♂️")
    
    # Display user info
    st.write(f"Logged in as: {st.session_state.user_info['email']}")
    st.write(f"Last login: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # # Navigation buttons
    # col1, col2, col3, col4 = st.columns(4)
    
    # with col1:
    #     if st.button("Dashboard", use_container_width=True):
    #         st.switch_page("pages/Dashboard.py")
    
    # with col2:
    #     if st.button("New Transaction", use_container_width=True):
    #         st.switch_page("pages/New Transactions.py")
    
    # with col3:
    #     if st.button("History", use_container_width=True):
    #         st.switch_page("pages/Transactions History.py")
    
    # with col4:
    #     if st.button("Statistics", use_container_width=True):
    #         st.switch_page("pages/Statistics.py")
    
    # Logout button
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.authentication_status = None
        st.rerun()

if __name__ == "__main__":
    login_signup_ui()