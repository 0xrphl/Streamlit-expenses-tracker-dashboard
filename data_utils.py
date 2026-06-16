import pandas as pd
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from config import SCOPE


def clean_amount(val):
    """Clean and convert amount values to float."""
    if pd.isna(val) or val == "":
        return 0.0
    try:
        return float(str(val).replace(",", "").strip())
    except Exception:
        return 0.0


def parse_date(val):
    """Parse date from various formats."""
    if pd.isna(val) or val == "":
        return None
    s = str(val).strip()
    fmts = ["%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y"]
    for fmt in fmts:
        try:
            return pd.to_datetime(s, format=fmt)
        except Exception:
            continue
    try:
        return pd.to_datetime(s)
    except Exception:
        return None


def process_table(df: pd.DataFrame) -> pd.DataFrame:
    """Process and normalize table data."""
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()

    # normalize columns
    if "amountCOP" in df.columns:
        df["amount"] = df["amountCOP"].apply(clean_amount)
    elif "amount" in df.columns:
        df["amount"] = df["amount"].apply(clean_amount)
    else:
        df["amount"] = 0.0

    if "date" in df.columns:
        df["date_parsed"] = df["date"].apply(parse_date)
    else:
        df["date_parsed"] = pd.NaT

    df = df.dropna(subset=["date_parsed"])
    df["event_lower"] = df.get("event", "").str.lower()
    df["is_expense"] = df["event_lower"] == "expense"
    df["is_income"] = df["event_lower"] == "income"
    return df


@st.cache_data(ttl=300)
def load_spreadsheet(sheet_url: str, credentials_path: str | None = None):
    """Load the spreadsheet and return gspread client + spreadsheet object."""
    if credentials_path:
        creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPE)
    else:
        if "gcp_service_account" not in st.secrets:
            st.error("Please configure Google Sheets credentials in .streamlit/secrets.toml")
            return None, None
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)

    client = gspread.authorize(creds)
    spreadsheet_id = sheet_url.split("/d/")[1].split("/")[0]
    spreadsheet = client.open_by_key(spreadsheet_id)
    return client, spreadsheet


@st.cache_data(ttl=300)
def load_tables(sheet_url: str, credentials_path: str | None = None):
    """Load Table 1 (all) and Table 2 (fixed) from the spreadsheet."""
    try:
        client, spreadsheet = load_spreadsheet(sheet_url, credentials_path)
        if spreadsheet is None:
            return None, None

        # Table 1: main
        ws_main = spreadsheet.worksheet("Table 1")
        records_main = ws_main.get_all_records()
        df_main = pd.DataFrame(records_main)

        # Table 2: fixed
        ws_fixed = spreadsheet.worksheet("Table 2 Fixed expenses")
        records_fixed = ws_fixed.get_all_records()
        df_fixed = pd.DataFrame(records_fixed)

        return process_table(df_main), process_table(df_fixed)
    except Exception as e:
        st.error(f"Error loading sheets: {e}")
        return None, None


def get_worksheet(sheet_url: str, credentials_path: str | None = None, sheet_name: str = "Table 1"):
    """Get worksheet object for writing. Not cached to avoid auth issues."""
    try:
        # Create fresh client for writing (don't reuse cached one)
        if credentials_path:
            creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPE)
        else:
            if "gcp_service_account" not in st.secrets:
                return None
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
        
        client = gspread.authorize(creds)
        spreadsheet_id = sheet_url.split("/d/")[1].split("/")[0]
        spreadsheet = client.open_by_key(spreadsheet_id)
        return spreadsheet.worksheet(sheet_name)
    except Exception as e:
        st.error(f"Error getting worksheet: {e}")
        return None


def apply_filters(df: pd.DataFrame, month, category, distribution, origin, event_filter, type_filter):
    """Apply filters to dataframe."""
    if df is None or df.empty:
        return pd.DataFrame()
    filtered = df.copy()
    if month != "All" and "month" in filtered.columns:
        # Handle both single month and list of months
        if isinstance(month, list):
            filtered = filtered[filtered["month"].isin(month)]
        else:
            filtered = filtered[filtered["month"] == month]
    if category != "All" and "transaction_category" in filtered.columns:
        filtered = filtered[filtered["transaction_category"] == category]
    if distribution != "All" and "distribution" in filtered.columns:
        filtered = filtered[filtered["distribution"] == distribution]
    if origin != "All" and "origin" in filtered.columns:
        filtered = filtered[filtered["origin"] == origin]
    if event_filter != "All":
        if event_filter == "Expense":
            filtered = filtered[filtered["is_expense"]]
        elif event_filter == "Income":
            filtered = filtered[filtered["is_income"]]
    if type_filter != "All" and "type_of_expense" in filtered.columns:
        filtered = filtered[filtered["type_of_expense"] == type_filter]
    return filtered


def money(x):
    """Format number as money."""
    return f"${x:,.0f} COP"


def calculate_month_from_date(date_str: str) -> str:
    """Calculate month string from date (format: YYYY-MM-MonthName)."""
    try:
        date_obj = parse_date(date_str)
        if date_obj:
            year = date_obj.year
            month_num = date_obj.month
            month_name = date_obj.strftime("%B")
            return f"{year}-{month_num:02d}-{month_name}"
    except Exception:
        pass
    # Also try if date_str is already a date object
    try:
        if hasattr(date_str, 'year'):
            year = date_str.year
            month_num = date_str.month
            month_name = date_str.strftime("%B")
            return f"{year}-{month_num:02d}-{month_name}"
    except Exception:
        pass
    return ""
