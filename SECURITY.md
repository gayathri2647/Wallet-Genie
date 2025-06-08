# Security Guidelines for WalletGenie

## Sensitive Files

The following files contain sensitive information and should **NEVER** be committed to a public repository:

1. `firebase_key.json` - Contains your Firebase service account private key
2. `firebase_config.json` - Contains your Firebase project API keys
3. `.env` - Contains environment variables with sensitive information
4. `.streamlit/secrets.toml` - Contains Streamlit secrets for deployment

## How to Handle Sensitive Files

1. Use the example templates provided:
   - `firebase_key.example.json`
   - `firebase_config.example.json`
   - `.env.example`
   - `.streamlit/secrets.toml.example`

2. Create your own copies with real credentials:
   ```
   cp firebase_key.example.json firebase_key.json
   cp firebase_config.example.json firebase_config.json
   cp .env.example .env
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

3. Edit these files with your actual credentials

4. Make sure these files are listed in `.gitignore` to prevent accidental commits

## If You've Already Committed Sensitive Files

If you've already committed sensitive files to a public repository:

1. **Immediately revoke and rotate all credentials**:
   - Go to the Firebase Console and generate new service account keys
   - Update API keys and other credentials

2. Remove the files from git history:
   ```
   git rm --cached firebase_key.json firebase_config.json .env .streamlit/secrets.toml
   git commit -m "Remove sensitive files from repository"
   git push
   ```

3. Consider using tools like BFG Repo-Cleaner or git-filter-branch to completely remove sensitive data from git history

## Best Practices

1. **Use environment variables** for sensitive information
2. **Use secret management services** for production deployments
3. **Regularly rotate credentials**
4. **Limit permissions** of service accounts to only what's necessary
5. **Monitor for unauthorized access** to your Firebase project

## Firebase Security Rules

Ensure your Firebase security rules are properly configured to restrict access to your data:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
      
      match /transactions/{transactionId} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }
      
      match /settings/{settingId} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }
    }
  }
}
```