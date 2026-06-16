# Configuration constants
import streamlit as st

# Google Sheets configuration
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


def get_sheet_url():
    """Get the Google Sheet URL from Streamlit secrets."""
    try:
        return st.secrets["sheet_url"]
    except Exception:
        return ""


def get_app_password():
    """Get the app password from Streamlit secrets."""
    try:
        return st.secrets["app_password"]
    except Exception:
        return "demo"


# Distribution options
# Customize these with your own partner names if desired
DISTRIBUTION_OPTIONS = ["50/50", "Partner 1", "Partner 2"]

# Transaction categories
TRANSACTION_CATEGORIES = [
    "Transportation",
    "Food and other groceries",
    "Entertainment and luxury",
    "Housing and basic services",
    "Health and taxes",
    "Education",
    "Pets",
    "Clothing and other basic expenses",
    "Memberships and subscriptions",
    "Traveling expenses",
    "Bank fees",
    "Crypto",
    "Payroll",
    "Codependents",
]

# Color scheme
COLORS = {
    "income": "#2ecc71",
    "expense": "#e74c3c",
    "primary": "#3b82f6",
    "secondary": "#2dd4bf",
    "background_dark": "#0f0f1e",
    "background_medium": "#1a1a2e",
    "text_light": "#e8e8e8",
    "text_dark": "#1a1a2e",
    "text_black": "#000000",
    "white": "#ffffff",
}
