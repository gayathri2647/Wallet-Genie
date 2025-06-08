# Streamlit Secrets Configuration Guide

This guide explains how to properly configure the secrets for your WalletGenie app in Streamlit Cloud.

## Required Secrets

Your Streamlit secrets must include **BOTH** of these sections:

### 1. Firebase Web Configuration

```toml
[firebase]
api_key = "your_api_key"
auth_domain = "your_project_id.firebaseapp.com"
project_id = "your_project_id"
storage_bucket = "your_project_id.appspot.com"
messaging_sender_id = "your_messaging_sender_id"
app_id = "your_app_id"
database_url = ""
```

### 2. Firebase Service Account

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

## How to Add Secrets in Streamlit Cloud

1. Go to your app settings in Streamlit Cloud
2. Navigate to the "Secrets" section
3. Click "Edit"
4. Paste both sections above with your actual values
5. Click "Save"

## Where to Find These Values

### Firebase Web Configuration

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click the gear icon (⚙️) next to "Project Overview" and select "Project settings"
4. Scroll down to "Your apps" section
5. Under the web app, click the config icon (</>) to view the configuration
6. Copy the values from the configuration object

### Firebase Service Account

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click the gear icon (⚙️) next to "Project Overview" and select "Project settings"
4. Go to the "Service accounts" tab
5. Click "Generate new private key"
6. Download the JSON file
7. Use the values from this JSON file in your secrets

## Troubleshooting

If you see errors like:

```
Error creating firebase_config.json: Missing required Firebase configuration: apiKey, authDomain, projectId, storageBucket, messagingSenderId, appId
```

This means your Firebase web configuration is missing or incomplete in the Streamlit secrets.

If you see errors like:

```
Error initializing Firebase Admin SDK: [Errno 2] No such file or directory: 'firebase_key.json'
```

This means your Firebase service account is missing in the Streamlit secrets.