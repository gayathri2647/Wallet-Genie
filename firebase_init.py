# firebase_init.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def init_firestore():
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
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        # Firebase already initialized
        pass
    return firestore.client()
