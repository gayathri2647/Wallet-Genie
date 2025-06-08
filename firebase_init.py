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
        cred = credentials.Certificate(service_account_info)
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