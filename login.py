import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore # Import auth and firestore
import pyrebase
import json
from datetime import datetime
import os
import sys
import requests

# Add current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Firebase Admin SDK initialization
try:
    if not firebase_admin._apps: # Check if app is already initialized
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
except ValueError:
    pass

# Pyrebase config
# Check if firebase_config.json exists
if os.path.exists("firebase_config.json"):
    with open("firebase_config.json") as f:
        config = json.load(f)
    firebase = pyrebase.initialize_app(config)
    auth_pb = firebase.auth()
    db_firestore = firestore.client() # Initialize Firestore client for user data
else:
    st.error("firebase_config.json not found. Please create it with your Firebase project configuration.")
    st.stop() # Stop the app if config is missing

# Streamlit page config
st.set_page_config(page_title="Wallet Genie - Login", page_icon="🔐", layout="centered")

# Session state defaults
for key in ["logged_in", "user_info", "authentication_status", "user_id", "email", "username"]: # Added "username"
    if key not in st.session_state:
        st.session_state[key] = None

# 🔒 Email/Password Login
def login_user(email, password):
    try:
        user = auth_pb.sign_in_with_email_and_password(email, password)
        account_info = auth_pb.get_account_info(user['idToken'])
        user_id = account_info['users'][0]['localId']

        # Get Firebase Auth user record to retrieve display_name
        firebase_user = auth.get_user(user_id)
        display_name = firebase_user.display_name if firebase_user.display_name else email.split('@')[0]

        st.session_state.logged_in = True
        st.session_state.email = email
        st.session_state.authentication_status = True
        st.session_state.user_id = user_id
        st.session_state.username = display_name # Store display name in session state
        st.success("Logged in successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

def signup_user(email, password, display_name): # Added display_name parameter
    try:
        user = auth_pb.create_user_with_email_and_password(email, password)
        user_id = user['localId'] # Get user ID from pyrebase response

        # Update Firebase Auth user profile with display name
        auth.update_user(user_id, display_name=display_name)

        # Store user's display name in Firestore (optional, but good for custom profiles)
        user_doc_ref = db_firestore.collection("users").document(user_id)
        user_doc_ref.set({"email": email, "username": display_name}, merge=True) # Store username in Firestore

        st.success("Account created successfully! Please login.")
    except Exception as e:
        st.error(f"Signup failed: {e}")

# Main UI
st.title("🔐 Welcome to Wallet Genie")
st.markdown("Please Login or Sign Up to continue.")

tab1, tab2 = st.tabs(["Login", "Sign Up"])

with tab1:
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login", use_container_width=True):
            if email and password:
                login_user(email, password)
            else:
                st.error("Please enter email and password")
    with col2:
        if st.button("Forgot Password?", use_container_width=True):
            if email:
                try:
                    auth_pb.send_password_reset_email(email)
                    st.success(f"Reset link sent to {email}")
                except Exception as e:
                    st.error(f"Error sending reset email: {e}")
            else:
                st.warning("Please enter your email")


with tab2:
    st.subheader("Sign Up")
    new_email = st.text_input("Email", key="signup_email")
    new_password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password")
    new_username = st.text_input("Username (e.g., 'JohnDoe')", key="signup_username") # New Username input

    if st.button("Create Account", use_container_width=True):
        if new_email and new_password and confirm_password and new_username: # Check for new_username
            if new_password == confirm_password:
                signup_user(new_email, new_password, new_username) # Pass new_username
            else:
                st.error("Passwords do not match")
        else:
            st.error("Please fill in all fields.")

# Run the UI
if __name__ == "__main__":
    if st.session_state.logged_in:
        st.success(f"Welcome, {st.session_state.username}!") # Display username after login
        st.write("You are logged in. Use the sidebar to navigate.")
        st.stop() # Stop further execution of login page if logged in