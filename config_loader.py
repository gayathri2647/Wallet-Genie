import os
from dotenv import load_dotenv
import json
import streamlit as st

def get_firebase_config():
    """
    Get Firebase configuration from environment variables or Streamlit secrets
    """
    # Check if running on Streamlit Cloud (secrets available)
    if hasattr(st, 'secrets') and 'firebase' in st.secrets:
        return {
            "apiKey": st.secrets.firebase.api_key,
            "authDomain": st.secrets.firebase.auth_domain,
            "projectId": st.secrets.firebase.project_id,
            "storageBucket": st.secrets.firebase.storage_bucket,
            "messagingSenderId": st.secrets.firebase.messaging_sender_id,
            "appId": st.secrets.firebase.app_id,
            "databaseURL": st.secrets.firebase.get("database_url", "")
        }
    # Otherwise use local .env file
    else:
        load_dotenv()
        return {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID"),
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "")
        }

def create_firebase_config_file():
    """
    Create firebase_config.json file from environment variables or Streamlit secrets
    """
    config = get_firebase_config()
    with open("firebase_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("firebase_config.json created successfully")