import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def init_firestore():
    """Initialize Firestore client"""
    # Check if running on Streamlit Cloud
    if hasattr(st, 'secrets') and 'firebase_service_account' in st.secrets:
        # Use service account from Streamlit secrets
        service_account_info = dict(st.secrets["firebase_service_account"])
        
        # Create a temporary file with the service account info
        with open("temp_key.json", "w") as f:
            json.dump(service_account_info, f)
        
        # Initialize Firebase with the temporary file
        cred = credentials.Certificate("temp_key.json")
        
        # Delete the temporary file
        os.remove("temp_key.json")
    else:
        # Use local service account file
        cred = credentials.Certificate("firebase_key.json")
    
    # Initialize Firebase if not already initialized
    if not firebase_admin._apps:
        try:
            firebase_admin.initialize_app(cred)
        except ValueError:
            # App already initialized
            pass
    
    # Return Firestore client
    return firestore.client()