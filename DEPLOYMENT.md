# ☁️ Streamlit Community Cloud Deployment Guide

This guide walks you through deploying the Household Expense Dashboard to **Streamlit Community Cloud** — a free hosting platform for Streamlit apps.

## Prerequisites

Before you start, make sure you have:

- ✅ A **GitHub account** with this repo pushed (you're reading this, so probably done!)
- ✅ A **Google Sheet** set up with the two required tabs (`Table 1` and `Table 2 Fixed expenses`)
- ✅ A **Google Cloud Service Account** with a JSON key file (see [README.md](README.md) step 3)
- ✅ The Google Sheet **shared with your service account email** (Editor permissions)

---

## Step-by-Step Deployment

### 1. Verify your GitHub repo

Make sure your code is pushed to GitHub and that `.streamlit/secrets.toml` is **NOT** committed (it's already in `.gitignore`).

Your repo should contain at minimum: `app.py`, `config.py`, `auth.py`, `chart_utils.py`, `data_utils.py`, `styles.py`, and `requirements.txt`.

### 2. Go to Streamlit Community Cloud

1. Visit **[share.streamlit.io](https://share.streamlit.io)**
2. Click **Sign in** → authenticate with your **GitHub account**
3. Once signed in, click **"New app"** in the top right

### 3. Configure your app

Fill in the deployment form:

| Field | Value |
|-------|-------|
| **Repository** | Select `your-username/Streamlit-expenses-tracker-dashboard` |
| **Branch** | `main` |
| **Main file path** | `app.py` |

> ⚡ **Before clicking Deploy**, click **"Advanced settings"** — this is where you add your secrets!

### 4. Add your secrets (most important step!)

In the **Advanced settings** panel, you'll see a **Secrets** text area. This is where you paste your TOML configuration — equivalent to `.streamlit/secrets.toml` for local development.

![Streamlit Cloud Secrets Configuration](screenshots/streamlit-cloud-secrets.png)

Paste the following into the Secrets text area, replacing all placeholder values with your actual credentials:

```toml
# 1. Your Google Sheet URL (copy from browser address bar)
sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"

# 2. Dashboard login password — choose any password you want.
#    This is what you and your partner will type to access the dashboard.
app_password = "your-secure-password"

# 3. Google Cloud Service Account credentials
#    Copy these values from the JSON key file you downloaded from Google Cloud Console.
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

#### How to fill in each value:

| Secret | Where to find it |
|--------|-----------------|
| `sheet_url` | Open your Google Sheet → copy the full URL from the browser address bar |
| `app_password` | Choose any password you want — this is what you type to log in to the dashboard |
| `project_id` | From your JSON key file → `"project_id"` field |
| `private_key_id` | From your JSON key file → `"private_key_id"` field |
| `private_key` | From your JSON key file → `"private_key"` field (keep all `\n` characters!) |
| `client_email` | From your JSON key file → `"client_email"` field |
| `client_id` | From your JSON key file → `"client_id"` field |
| Other fields | Copy exactly as shown above (they're the same for everyone) |

> ⚠️ **Critical:** The `private_key` field must include the `\n` characters for line breaks — copy it exactly as it appears in the JSON file, wrapped in quotes.

> 💡 **Tip:** Open your JSON key file in a text editor, and copy each value one by one into the TOML format above.

### 5. Deploy!

Click **"Deploy!"** and wait for the app to build. This usually takes 1-2 minutes.

Once deployed, you'll get a public URL like:
```
https://your-app-name.streamlit.app
```

Open it, type your `app_password`, and you're in! 🎉

### 6. Update secrets after deployment (if needed)

If you need to change secrets after deploying:

1. Go to your app on [share.streamlit.io](https://share.streamlit.io)
2. Click the **⋮** (three dots) menu → **Settings**
3. Go to the **Secrets** tab
4. Edit your secrets and click **Save**
5. The app will automatically reboot with the new secrets

---

## Verify Google Sheets Permissions

If the dashboard shows "Unable to load data", double-check that your Google Sheet is shared with the service account:

1. Open your Google Sheet
2. Click **Share**
3. Add your service account email (the `client_email` from your JSON key, looks like: `your-sa@your-project.iam.gserviceaccount.com`)
4. Give it **Editor** permissions (needed for the "Add Transaction" feature)
5. Click **Send**

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "No Google Sheet URL configured" | `sheet_url` is missing from secrets | Add `sheet_url` to your Streamlit Cloud secrets |
| "Please configure Google Sheets credentials" | `[gcp_service_account]` section is missing or malformed | Verify the TOML format in secrets — check for missing quotes or brackets |
| "Unable to load data. Check credentials and sharing" | Service account doesn't have access to the sheet | Share the Google Sheet with your service account email (Editor access) |
| "Invalid credentials" | `private_key` is malformed | Make sure the `private_key` includes all `\n` characters and is wrapped in quotes |
| "Wrong password" at login | `app_password` doesn't match | Check `app_password` in secrets — it's case-sensitive |
| App crashes on startup | Missing dependency | Make sure `requirements.txt` is in the repo root |
| Sheets tabs not found | Tab names don't match | Verify tabs are named exactly `Table 1` and `Table 2 Fixed expenses` |

---

## Local Development

For local development (running on your own machine):

1. Copy the template: 
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Fill in your actual credentials in `.streamlit/secrets.toml`
3. Run:
   ```bash
   streamlit run app.py
   ```

**⚠️ Never commit `.streamlit/secrets.toml` to git** — it contains your private credentials and is already in `.gitignore`.
