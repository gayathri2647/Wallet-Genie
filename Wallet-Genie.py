import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore # Import auth and firestore
import pyrebase
import json
import os
import sys
from dotenv import load_dotenv
import requests
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))



try:
    if not firebase_admin._apps: # Check if app is already initialized
        cred = credentials.Certificate({
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
        #print("hehe :",st.secrets["firebase"]["project_id"])

        firebase_admin.initialize_app(cred)
except ValueError:
    logging.error("Firebase app already initialized")
    pass
except Exception as e:
    logging.error(f"Error initializing Firebase Admin SDK: {e}")
    st.error("Failed to initialize authentication service. Please try again later.")
    st.stop()


# Load Firebase config
try:
    
    config = {
        "apiKey": st.secrets["firebase"]["api_key"],
        "authDomain": st.secrets["firebase"]["auth_domain"],
        "projectId": st.secrets["firebase"]["project_id"],
        "storageBucket": st.secrets["firebase"]["storage_bucket"],
        "messagingSenderId": st.secrets["firebase"]["messaging_sender_id"],
        "appId": st.secrets["firebase"]["app_id"],
        "databaseURL": st.secrets["firebase"]["database_url"]
        }
    firebase = pyrebase.initialize_app(config)
    auth_pb = firebase.auth()
    db_firestore = firestore.client() # Initialize Firestore client for user data
except Exception as e:
    logging.error(f"Error initializing Pyrebase: {e}")
    st.error("Failed to connect to authentication service. Please try again later.")
    st.stop()

# Streamlit page config
st.set_page_config(page_title="Wallet Genie - Login", page_icon="🔐", layout="centered")

# Session state defaults
for key in ["logged_in", "user_info", "authentication_status", "user_id", "email", "username", "show_login_ui"]:
    if key not in st.session_state:
        st.session_state[key] = None
        
# Set show_login_ui to True by default if it's None
if st.session_state.show_login_ui is None:
    st.session_state.show_login_ui = True

# 🔒 Email/Password Login
def login_user(email, password):
    #print(email,password)
    try:
        user = auth_pb.sign_in_with_email_and_password(email, password)
        account_info = auth_pb.get_account_info(user['idToken'])
        user_id = account_info['users'][0]['localId']
        #print(auth.idToken.toString())
        # Get Firebase Auth user record to retrieve display_name
        firebase_user = auth.get_user(user_id)
        display_name = firebase_user.display_name if firebase_user.display_name else email.split('@')[0]

        st.session_state.logged_in = True
        st.session_state.email = email
        st.session_state.authentication_status = True
        st.session_state.user_id = user_id
        st.session_state.username = display_name # Store display name in session state
        st.session_state.show_login_ui = False # Hide login UI after successful login
        
        # Log successful login but don't expose details
        logging.info(f"Successful login for user ID: {user_id}")
        
        st.success("Logged in successfully! Redirecting to dashboard...")
        # Use JavaScript to redirect to the Dashboard page after a short delay
        st.switch_page("pages/2_Dashboard.py")
        st.markdown("""
            <script>
                setTimeout(function() {
                    window.location.href = "/pages/2_Dashboard";
                }, 1500);
            </script>
        """, unsafe_allow_html=True)
        st.rerun()
    except Exception as e:
        # Log detailed error for debugging
        logging.error(f"Login error: {str(e)}")
        # st.error(f"Error : {str(e)}")
        # Show user-friendly message
        st.error("Login failed. Please check your email and password.")
        # try:
        #     error_json = e.args[0].response.json()
        #     error_message = error_json['error']['message']
        #     st.error(f"Login failed: {error_message}")
        #     logging.error(f"Login failed: {error_message}")
        # except Exception as inner_e:
        #     # fallback if we can't parse the error JSON
        #     st.error("Login failed. Please check your email and password.")
        #     logging.error(f"Unexpected login error: {str(inner_e)} | Original error: {str(e)}")

def signup_user(email, password, display_name): # Added display_name parameter
    try:
        user = auth_pb.create_user_with_email_and_password(email, password)
        user_id = user['localId'] # Get user ID from pyrebase response

        # Update Firebase Auth user profile with display name
        auth.update_user(user_id, display_name=display_name)

        # Store user's display name in Firestore (optional, but good for custom profiles)
        user_doc_ref = db_firestore.collection("users").document(user_id)
        user_doc_ref.set({"email": email, "username": display_name}, merge=True) # Store username in Firestore

        logging.info(f"New user account created: {user_id}")
        st.success("Account created successfully! Please login.")
    except Exception as e:
        logging.error(f"Signup error: {str(e)}")
       # st.error(f"Error : {str(e)}")
        
        st.error("Account creation failed. Please try again with a different email or stronger password.")

# Main UI
if st.session_state.logged_in and not st.session_state.show_login_ui:
    # If user is logged in but still on login page, redirect to dashboard
    st.success(f"Welcome, {st.session_state.username}!")
    st.info("You are already logged in. Redirecting to dashboard...")
    # st.switch_page("pages/2_Dashboard.py")
    
    # Use JavaScript to redirect to the Dashboard page
    st.markdown("""
        <script>
            window.location.href = "/pages/2_Dashboard";
        </script>
    """, unsafe_allow_html=True)
else:
    # Show login UI
    st.title("Welcome to Wallet Genie")
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
                        logging.error(f"Password reset error: {str(e)}")
                        st.error("Error sending reset email. Please check if the email is registered.")
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

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))