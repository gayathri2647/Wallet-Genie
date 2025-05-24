# firebase_init.py
import firebase_admin
from firebase_admin import credentials, firestore

def init_firestore():
    cred = credentials.Certificate("firebase_key.json")
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        # Firebase already initialized
        pass
    return firestore.client()
