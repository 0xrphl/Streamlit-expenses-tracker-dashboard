# 💰 Household Expense Dashboard

A real-time **Streamlit** dashboard for couples / households to track shared expenses, income, and debts — powered by **Google Sheets** as a database and the **Google Cloud API** for authentication.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red) ![License](https://img.shields.io/badge/License-MIT-green)

---

## 📸 Preview

### Main Dashboard — KPIs, expense breakdown, and timeline
![Main Dashboard](screenshots/dashboard-main.png)

### Detailed Charts — Scroll down for category analysis, Sankey debt diagram, and more
![Dashboard Scroll Down](screenshots/dashboard-scroll-down.png)

### Add Transactions — Use the sidebar form to add new expenses or income directly
![Add Transaction Sidebar](screenshots/dashboard-add-transaction.png)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Real-time sync** | Reads live data from Google Sheets (no local DB needed) |
| ➕ **Add transactions** | Insert new expenses / income directly from the dashboard |
| 💸 **Debt Sankey diagram** | Visual 18-case analysis of who owes what |
| 📈 **Interactive charts** | Timeline, pie, bar charts with Plotly |
| 🔍 **Advanced filters** | Month, year, category, distribution, origin, type |
| 📌 **Fixed expense tracking** | Budget vs. actual with % paid indicators |
| 🔐 **Password protection** | Simple passkey auth (configurable via secrets) |
| 📥 **CSV export** | Download filtered data |
| ☁️ **Cloud-ready** | Deploy to Streamlit Community Cloud in minutes |

---

## 📐 Architecture

```
Google Sheets (DB)  ──▶  Google Cloud API  ──▶  Streamlit App (Dashboard)
     │                        │                        │
     ├─ Table 1 (all tx)      ├─ Service Account       ├─ app.py (main)
     └─ Table 2 (fixed)       └─ Sheets + Drive API    ├─ config.py
                                                        ├─ chart_utils.py
                                                        ├─ auth.py
                                                        └─ data_utils.py
```

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/0xrphl/Streamlit-expenses-tracker-dashboard.git
cd Streamlit-expenses-tracker-dashboard
pip install -r requirements.txt
```

### 2. Set up the Google Sheet (your database)

Your Google Sheet acts as the database. It needs **two tabs** with specific column headers.

#### Option A — Copy the template (fastest)

1. Open the **[Template Sheet](https://docs.google.com/spreadsheets/d/1RCLC-GYdQeORyArb3X28P2F0TSWhK-XsE4eisYEQ3R0/edit?gid=0#gid=0)**
2. Click **File → Make a copy**
3. You now have your own sheet — copy the URL for later

#### Option B — Create from scratch

Create a Google Sheet with **two tabs**:

**Tab: `Table 1`** (all transactions)

| Column | Description | Example |
|--------|-------------|---------|
| `event` | "Expense" or "Income" | Expense |
| `date` | Date (MM/DD/YYYY) | 01/15/2026 |
| `month` | Year-month label | 2026-01-January |
| `type_of_expense` | "Fixed" or "One time" | Fixed |
| `transaction_category` | Category name | Food and other groceries |
| `amountCOP` | Amount in COP | 150,000 |
| `distribution` | Who pays: "50/50", "Partner 1", or "Partner 2" | 50/50 |
| `details` | Description | Groceries |
| `origin` | Source account | Savings account Partner 2 |

**Tab: `Table 2 Fixed expenses`** (monthly budget)

| Column | Description | Example |
|--------|-------------|---------|
| `event` | Always "Expense" | Expense |
| `date` | Budget start date | 1/1/2026 |
| `month` | Budget month | 2026-01-January |
| `type_of_expense` | Always "Fixed" | Fixed |
| `transaction_category` | Category | Housing and basic services |
| `amountCOP` | Budgeted amount | 1,800,000 |
| `details` | Expense name | Mortgage |
| `distribution` | Who pays | 50/50 |
| `origin` | Account | Savings account Partner 2 |
| `amount_paid%` | % already paid | 95.2 |
| `one_payment` | TRUE/FALSE | TRUE |
| `months_valid` | How many months | 1 |

Here's what your Google Sheet should look like with data:

![Google Sheet Table 1](screenshots/google-sheet-table1.png)

#### Load demo data (optional)

To quickly populate the sheet with sample data, open your sheet and go to **Extensions → Apps Script**, then paste the code from [`demo_data_appscript.js`](demo_data_appscript.js) and run the `populateDemoData` function.

---

### 3. Set up Google Cloud API

You need a **Google Cloud Service Account** to let the Streamlit app read/write your Google Sheet.

1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**
2. Create a new project (or select an existing one)
3. **Enable APIs:**
   - Navigate to **APIs & Services → Library**
   - Search and enable **Google Sheets API**
   - Search and enable **Google Drive API**
4. **Create a Service Account:**
   - Go to **IAM & Admin → Service Accounts**
   - Click **Create Service Account**
   - Name it (e.g., `expense-dashboard`)
   - Click **Create and Continue** → skip role → **Done**
5. **Create a JSON key:**
   - Click on the service account you just created
   - Go to the **Keys** tab
   - Click **Add Key → Create new key → JSON**
   - Download the JSON file — **keep it safe, never commit it!**
6. **Share the Google Sheet** with the service account:
   - Open your Google Sheet
   - Click **Share**
   - Paste the `client_email` from the JSON file (looks like `xxx@xxx.iam.gserviceaccount.com`)
   - Set permission to **Editor** (needed for the "Add Transaction" feature)
   - Click **Send**

---

### 4. Configure secrets (local development)

The app uses Streamlit's secrets management. There are **three** things you need to configure:

| Secret | What it does |
|--------|-------------|
| `sheet_url` | The full URL of your Google Sheet |
| `app_password` | The password users type to log in to the dashboard |
| `[gcp_service_account]` | Your Google Cloud Service Account credentials |

```bash
# Create the secrets file
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and fill in your values:

```toml
# The URL of your Google Sheet (copy from browser)
sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"

# The password to access the dashboard — choose any password you want.
# Users will be prompted to enter this when they open the app.
# Example: "mybudget2026", "household!", etc.
app_password = "your-secure-password"

# Paste your Google Cloud Service Account credentials below.
# These come from the JSON key file you downloaded in step 3.
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-sa@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
universe_domain = "googleapis.com"
```

> 💡 **How to fill `[gcp_service_account]`:** Open the JSON key file you downloaded from Google Cloud. Copy each field into the TOML format above. The `private_key` must keep the `\n` line breaks exactly as they appear in the JSON.

> ⚠️ **Never commit `secrets.toml`** — it's already in `.gitignore`.

---

### 5. Run locally

```bash
streamlit run app.py
```

The dashboard opens at **http://localhost:8501**. Enter the password you set in `app_password` to log in.

---

## ☁️ Deploy to Streamlit Community Cloud

1. Push your code to **GitHub** (make sure `secrets.toml` is NOT included)
2. Go to **[share.streamlit.io](https://share.streamlit.io)**
3. Sign in with GitHub → Click **New app**
4. Select your repo and set main file to `app.py`
5. Click **Advanced settings** → go to the **Secrets** section
6. Paste your entire `secrets.toml` content (including `sheet_url`, `app_password`, and `[gcp_service_account]`):

![Streamlit Cloud Secrets Modal](screenshots/streamlit-cloud-secrets.png)

```toml
sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
app_password = "your-password"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
universe_domain = "googleapis.com"
```

7. Click **Deploy!** 🎉

> 📌 **Note about `app_password`:** This is a simple shared password that protects your dashboard from public access. It's not meant for multi-user auth — just a passkey that you and your partner share. You can change it anytime by updating the secret in Streamlit Cloud settings.

For more details, see [`DEPLOYMENT.md`](DEPLOYMENT.md).

---

## 🛠 Customization

### Change partner names

By default the distribution options are `"Partner 1"` and `"Partner 2"`. To customize:

1. Edit `config.py`:
   ```python
   DISTRIBUTION_OPTIONS = ["50/50", "Alice", "Bob"]
   ```
2. Update your Google Sheet data to match the new names
3. Update the origin accounts in your sheet (e.g., `"Savings account Alice"`)

### Add or change categories

Edit the `TRANSACTION_CATEGORIES` list in `config.py`.

### Change currency

Search for `COP` in `app.py` and replace with your currency code.

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No Google Sheet URL configured" | Set `sheet_url` in `.streamlit/secrets.toml` |
| "Please configure Google Sheets credentials" | Add `[gcp_service_account]` to secrets |
| "Unable to load data" | Share the sheet with the service account email |
| "Error getting worksheet" | Give the service account **Editor** (not Viewer) access |
| "Error loading sheets" | Check that the sheet has tabs named `Table 1` and `Table 2 Fixed expenses` |
| Auth issues after deploy | Verify the `private_key` includes `\n` characters |
| "Wrong password" | Check `app_password` in your secrets — it's case-sensitive |

---

## 📁 Project Structure

```
├── app.py                          # Main Streamlit app
├── config.py                       # Configuration (categories, colors, helpers)
├── auth.py                         # Authentication logic
├── chart_utils.py                  # Plotly chart builders + Sankey diagram
├── data_utils.py                   # Data loading & processing utilities
├── styles.py                       # Custom CSS styles
├── requirements.txt                # Python dependencies
├── demo_data_appscript.js          # Google Apps Script to populate demo data
├── screenshots/                    # Screenshots for README
│   ├── dashboard-main.png          # Main dashboard view
│   ├── dashboard-scroll-down.png   # Charts section when scrolling down
│   ├── dashboard-add-transaction.png # Sidebar form for adding transactions
│   ├── google-sheet-table1.png     # Google Sheet data structure
│   └── streamlit-cloud-secrets.png # Streamlit Cloud secrets configuration
├── .streamlit/
│   └── secrets.toml.example        # Template for secrets (copy to secrets.toml)
├── .gitignore                      # Excludes secrets, credentials, caches
├── DEPLOYMENT.md                   # Streamlit Cloud deployment guide
└── README.md                       # This file
```

---

## 📄 License

This project is open source and available for personal use. Feel free to fork, modify, and use it for your own household budgeting!
