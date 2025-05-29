import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
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
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
except ValueError:
    pass

# Pyrebase config
with open("firebase_config.json") as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config)
auth_pb = firebase.auth()

# Streamlit page config
st.set_page_config(page_title="Wallet Genie - Login", page_icon="🔐", layout="centered")

# Session state defaults
for key in ["logged_in", "user_info", "authentication_status", "user_id", "email"]:
    if key not in st.session_state:
        st.session_state[key] = None

# 🔒 Email/Password Login
def login_user(email, password):
    try:
        user = auth_pb.sign_in_with_email_and_password(email, password)
        account_info = auth_pb.get_account_info(user['idToken'])
        user_id = account_info['users'][0]['localId']
        st.session_state.update({
            "user_info": user,
            "logged_in": True,
            "authentication_status": True,
            "email": email,
            "user_id": user_id
        })
        st.success("Login successful!")
        st.balloons()
        st.switch_page("pages/2_Dashboard.py")
    except Exception as e:
        st.session_state.authentication_status = False
        st.error("Login failed. Please check your credentials.")

# 🧾 Sign Up
def signup_user(email, password):
    try:
        user = auth_pb.create_user_with_email_and_password(email, password)
        auth_pb.send_email_verification(user['idToken'])
        st.success("Account created! Please verify your email.")
        st.session_state.update({
            "user_info": user,
            "logged_in": True,
            "authentication_status": True,
            "email": email
        })
        st.switch_page("pages/Dashboard.py")
    except Exception as e:
        st.session_state.authentication_status = False
        st.error(f"Signup failed: {e}")

# 🟢 Google Login via OAuth
def google_login():
    firebase_web_api_key = config["apiKey"]
    st.markdown("Login via Google requires a pop-up OAuth sign-in page.")
    oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={config['authDomain'].split('.')[0]}&redirect_uri=http://localhost&response_type=token&scope=email"
    st.markdown(f"[Click here to sign in with Google]({oauth_url})")
    # NOTE: To implement full OAuth with token exchange, you must host and handle redirect URI (not fully supported in Streamlit alone).

# 👤 UI for logged-in user
def display_logged_in_ui():
    st.title("Welcome to Wallet Genie! 🧞‍♂️")
    st.write(f"Logged in as: {st.session_state.email}")
    st.write(f"Last login: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if st.button("Logout", use_container_width=True):
        for key in ["logged_in", "user_info", "authentication_status", "user_id", "email"]:
            st.session_state[key] = None
        st.rerun()

# 🧩 Login/Signup Tabs
def login_signup_ui():
    if st.session_state.logged_in:
        display_logged_in_ui()
        return

    st.title("Wallet Genie 🧞‍♂️")
    st.markdown("Your personal finance assistant")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        col1, col2, col3 = st.columns([1, 1, 2])
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
        with col3:
            if st.button("Login with Google", use_container_width=True):
                google_login()

    with tab2:
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Create Account", use_container_width=True):
            if new_email and new_password and confirm_password:
                if new_password == confirm_password:
                    signup_user(new_email, new_password)
                else:
                    st.error("Passwords do not match")
            else:
                st.error("Please fill in all fields")

# Run the UI
if __name__ == "__main__":
    login_signup_ui()
