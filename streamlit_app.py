import streamlit as st
import sys
import os
import logging
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Firebase Admin SDK
try:
    if not firebase_admin._apps:
        if hasattr(st, 'secrets') and 'firebase_service_account' in st.secrets:
            # Use service account from Streamlit secrets
            service_account_info = dict(st.secrets["firebase_service_account"])
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
            logging.info("Firebase initialized using Streamlit secrets")
        else:
            logging.error("No Firebase service account found in Streamlit secrets")
            st.error("Firebase service account not found. Please add it to Streamlit secrets.")
            st.stop()
except Exception as e:
    logging.error(f"Error initializing Firebase: {e}")
    st.error(f"Failed to initialize Firebase: {e}")
    st.stop()

# Check for Firebase web config
if not hasattr(st, 'secrets') or 'firebase' not in st.secrets:
    logging.error("No Firebase web config found in Streamlit secrets")
    st.error("""
    Firebase web configuration not found in Streamlit secrets.
    
    Please add the following to your Streamlit secrets:
    
    [firebase]
    api_key = "your_api_key"
    auth_domain = "your_project_id.firebaseapp.com"
    project_id = "your_project_id"
    storage_bucket = "your_project_id.appspot.com"
    messaging_sender_id = "your_messaging_sender_id"
    app_id = "your_app_id"
    database_url = ""
    """)
    st.stop()

# Verify Firebase web config has required fields
required_keys = ["api_key", "auth_domain", "project_id", "storage_bucket", "messaging_sender_id", "app_id"]
missing_keys = [key for key in required_keys if not hasattr(st.secrets.firebase, key) or not getattr(st.secrets.firebase, key)]
if missing_keys:
    error_msg = f"Missing required Firebase configuration: {', '.join(missing_keys)}"
    logging.error(error_msg)
    st.error(f"Firebase configuration incomplete. {error_msg}")
    st.stop()

# If all checks pass, import the main app
from Wallet_Genie import *