import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import logging

def init_firestore():
    """Initialize Firestore client"""
    # Check if running on Streamlit Cloud
    if hasattr(st, 'secrets') and 'firebase_service_account' in st.secrets:
        # Use service account from Streamlit secrets
        try:
            service_account_info = dict(st.secrets["firebase_service_account"])
            cred = credentials.Certificate(service_account_info)
        except Exception as e:
            logging.error(f"Error loading Firebase credentials from secrets: {e}")
            st.error("Failed to load Firebase credentials from secrets.")
            st.stop()
    elif os.path.exists("firebase_key.json"):
        # Use local service account file if it exists
        try:
            cred = credentials.Certificate("firebase_key.json")
        except Exception as e:
            logging.error(f"Error loading Firebase credentials from file: {e}")
            st.error("Failed to load Firebase credentials from file.")
            st.stop()
    else:
        logging.error("No Firebase credentials found")
        st.error("Firebase credentials not found. Please check your configuration.")
        st.stop()
    
    # Initialize Firebase if not already initialized
    if not firebase_admin._apps:
        try:
            firebase_admin.initialize_app(cred)
        except ValueError:
            # App already initialized
            pass
        except Exception as e:
            logging.error(f"Error initializing Firebase: {e}")
            st.error("Failed to initialize Firebase.")
            st.stop()
    
    # Return Firestore client
    return firestore.client()