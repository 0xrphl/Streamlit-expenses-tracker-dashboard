# ☁️ Streamlit Community Cloud Deployment Guide

## Prerequisites

- A GitHub repository with this code pushed
- A Google Service Account with access to your Google Sheet
- The service account JSON credentials file from Google Cloud Console

## Steps to Deploy

### 1. Push to GitHub

Make sure your code is pushed to GitHub and that `.streamlit/secrets.toml` is **NOT** committed (it's in `.gitignore`).

### 2. Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Select your repository
5. Set the main file path: `app.py`
6. Click **Advanced settings** before deploying

### 3. Configure Secrets

**This is the most important step!**

1. In **Advanced settings** (or after deployment in **App settings → Secrets**), paste:

```toml
sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
app_password = "your-secure-password"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

**Important Notes:**
- Replace all `your-*` placeholders with actual values from your Google Service Account JSON file
- The `private_key` field must include the `\n` characters for line breaks
- Make sure the entire section is under `[gcp_service_account]`
- `sheet_url` and `app_password` go **above** the `[gcp_service_account]` section
- Double-check that there are no syntax errors

### 4. Verify Google Sheets Permissions

Make sure your Google Service Account has been granted access to your spreadsheet:

1. Open your Google Sheet
2. Click **Share**
3. Add your service account email (looks like: `your-sa@your-project.iam.gserviceaccount.com`)
4. Give it **Editor** permissions (needed for adding transactions)

### 5. Deploy!

Click **Deploy** and wait for the app to start.

## Troubleshooting

### Error: "No Google Sheet URL configured"
- Your `sheet_url` is missing from secrets
- Go to App settings → Secrets and add it

### Error: "Please configure Google Sheets credentials"
- Your `[gcp_service_account]` section is missing or malformed
- Go to App settings → Secrets and verify the format

### Error: "Unable to load data. Check credentials and sharing"
- Your service account doesn't have access to the Google Sheet
- Share the sheet with your service account email

### Error: "Invalid credentials"
- Check that your `private_key` includes the `\n` characters
- Verify all fields match your service account JSON file exactly

## Local Development

For local development:

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Fill in your actual credentials
3. Run `streamlit run app.py`

**⚠️ Never commit `.streamlit/secrets.toml` to git** — it's already in `.gitignore`.
