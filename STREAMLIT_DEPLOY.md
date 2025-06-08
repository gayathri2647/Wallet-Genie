# Streamlit Deployment Guide for WalletGenie

This guide explains how to deploy WalletGenie to Streamlit Cloud.

## Prerequisites

1. A GitHub repository with your WalletGenie code
2. A Firebase project with Firestore database
3. A Streamlit Cloud account (https://streamlit.io/cloud)

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository has the following files:
- `requirements.txt` - Lists all Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `.streamlit/secrets.toml.example` - Template for secrets
- `runtime.txt` - Specifies Python version

### 2. Set Up Secrets in Streamlit Cloud

1. Log in to Streamlit Cloud
2. Create a new app pointing to your GitHub repository
3. Go to "Advanced Settings" > "Secrets"
4. Add your Firebase credentials in the following format:

```toml
[firebase]
api_key = "your_api_key_here"
auth_domain = "your_project_id.firebaseapp.com"
project_id = "your_project_id"
storage_bucket = "your_project_id.appspot.com"
messaging_sender_id = "your_sender_id"
app_id = "your_app_id"
database_url = ""
```

5. Add your Firebase service account key in the following format:

```toml
[firebase_service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project-id.iam.gserviceaccount.com"
```

### 3. Update Your Code for Streamlit Cloud

You need to modify `firebase_init.py` to read the service account key from Streamlit secrets:

```python
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
        firebase_admin.initialize_app(cred)
    
    # Return Firestore client
    return firestore.client()
```

### 4. Deploy Your App

1. In Streamlit Cloud, click "Deploy"
2. Select your repository, branch, and main file (`Wallet-Genie.py`)
3. Click "Deploy"

### 5. Verify Deployment

1. Wait for the deployment to complete
2. Test your app by logging in and verifying that all features work
3. Check the logs for any errors

## Troubleshooting

If you encounter issues:

1. Check the Streamlit Cloud logs for error messages
2. Verify that all secrets are correctly set up
3. Make sure your Firebase project has the correct security rules
4. Ensure all dependencies are listed in `requirements.txt`