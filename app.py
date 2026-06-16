import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from config import (
    SCOPE,
    DISTRIBUTION_OPTIONS,
    TRANSACTION_CATEGORIES,
    get_sheet_url,
    get_app_password,
)

# Page configuration
st.set_page_config(
    page_title="Budget & Expenses Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional styling
st.markdown(
    """
    <style>
    /* Main app styling */
    .stApp { 
        color: #e8e8e8;
        background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
    }
    
    /* Metric styling */
    .stMetric {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a7b 100%);
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stMetricLabel, .stMetricDelta, .st-emotion-cache-1xarl3l, .st-emotion-cache-10trblm { 
        color: #e8e8e8 !important;
        font-weight: 600;
        font-size: 0.9rem !important;
    }
    
    .stMetricValue {
        font-size: 1.3rem !important;
    }
    
    .st-emotion-cache-1v0mbdj svg text { 
        fill: #e8e8e8 !important; 
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(90deg, #3b82f6 0%, #2dd4bf 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 1.8rem !important;
        margin-bottom: 0.3rem !important;
    }
    
    h2 {
        color: #3b82f6;
        font-weight: 600;
        font-size: 1.3rem !important;
        margin-top: 0.8rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h3 {
        color: #3b82f6;
        font-weight: 600;
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.3rem !important;
    }
    
    /* Caption/subtitle styling */
    .stMarkdown p {
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1e 100%);
        border-right: 2px solid rgba(59, 130, 246, 0.3);
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Card-like containers */
    .element-container {
        transition: all 0.3s ease;
    }
    
    /* Custom divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #3b82f6 50%, transparent 100%);
        margin: 2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------
# Data loading utilities
# -----------------------
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


def clean_amount(val):
    if pd.isna(val) or val == "":
        return 0.0
    try:
        return float(str(val).replace(",", "").strip())
    except Exception:
        return 0.0


def parse_date(val):
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
    try:
        if hasattr(date_str, "year"):
            year = date_str.year
            month_num = date_str.month
            month_name = date_str.strftime("%B")
            return f"{year}-{month_num:02d}-{month_name}"
    except Exception:
        pass
    return ""


# -----------------------
# Dashboard helpers
# -----------------------
def apply_filters(df: pd.DataFrame, month, category, distribution, origin, event_filter, type_filter):
    if df is None or df.empty:
        return pd.DataFrame()
    filtered = df.copy()
    if month != "All" and "month" in filtered.columns:
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
    return f"${x:,.0f} COP"


# -----------------------
# Authentication
# -----------------------
def check_auth():
    """Check if user is authenticated. Returns True if authenticated."""
    app_password = get_app_password()
    query_params = st.query_params
    if "auth" in query_params and query_params["auth"] == app_password:
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = True
        return True

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated


def login_page():
    """Display login page."""
    app_password = get_app_password()
    st.title("🔐 Login Required")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Enter Passkey")
        passkey = st.text_input("Passkey", type="password", label_visibility="collapsed", placeholder="Enter passkey")

        if st.button("Login", type="primary", use_container_width=True):
            if passkey == app_password:
                st.session_state.authenticated = True
                st.query_params["auth"] = app_password
                st.rerun()
            else:
                st.error("❌ Incorrect passkey. Please try again.")

        st.markdown("---")
        st.caption("Enter the passkey to access the dashboard")


# -----------------------
# Main app
# -----------------------
def main():
    # Check authentication first
    if not check_auth():
        login_page()
        return

    SHEET_URL = get_sheet_url()
    if not SHEET_URL:
        st.error("⚠️ No Google Sheet URL configured. Please set `sheet_url` in your `.streamlit/secrets.toml` file.")
        st.code(
            'sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"',
            language="toml",
        )
        return

    st.title("💰 Budget & Expenses Dashboard")
    st.caption("Live data from Google Sheets (Table 1: all transactions, Table 2: fixed expenses)")
    st.markdown("---")

    # Sidebar configuration (filters only)
    with st.sidebar:
        st.header("Filters")
        if st.button("🔄 Refresh data", type="primary"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")

        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.query_params.clear()
            st.rerun()

        st.markdown("---")

    df_main, df_fixed = load_tables(SHEET_URL, None)

    if df_main is None:
        st.error("Unable to load data. Check credentials and sharing.")
        return

    # Add new row form in sidebar
    with st.sidebar:
        st.markdown("---")

        if "show_add_form" not in st.session_state:
            st.session_state.show_add_form = False

        if st.button("➕ Add New Transaction", use_container_width=True, type="primary"):
            st.session_state.show_add_form = not st.session_state.show_add_form
            st.rerun()

        if st.session_state.show_add_form:
            with st.expander("📝 Transaction Form", expanded=True):
                event_type = st.selectbox("Event", ["Expense", "Income"], key="form_event")
                transaction_date = st.date_input("Date", value=datetime.now().date(), key="form_date")
                type_of_expense = st.selectbox("Type of Expense", ["", "Fixed", "One time"], key="form_type")
                transaction_category = st.selectbox("Category", TRANSACTION_CATEGORIES, key="form_category")
                amount = st.number_input("Amount (COP)", min_value=0.0, step=1000.0, key="form_amount")
                distribution = st.selectbox("Distribution", DISTRIBUTION_OPTIONS, key="form_distribution")

                # Details - depends on type
                details = ""
                if type_of_expense == "Fixed":
                    st.markdown("**Details** (Select from fixed expenses)")
                    if df_fixed is not None and not df_fixed.empty and "details" in df_fixed.columns:
                        fixed_details = sorted(df_fixed["details"].dropna().unique().tolist())
                        if fixed_details:
                            details = st.selectbox("Select expense", fixed_details, key="form_details", label_visibility="collapsed")
                        else:
                            details = st.text_input("No fixed expenses - enter manually", key="form_details", label_visibility="collapsed")
                    else:
                        details = st.text_input("No fixed expenses - enter manually", key="form_details", label_visibility="collapsed")
                elif type_of_expense == "One time":
                    st.markdown("**Details** (Type freely)")
                    details = st.text_input("Enter expense details", value="", key="form_details", label_visibility="collapsed", placeholder="Type your expense details here...")
                else:
                    st.info("ℹ️ Please select a Type of Expense to continue")

                # Origin
                if "origin" in df_main.columns:
                    origins = sorted(df_main["origin"].dropna().unique().tolist())
                    if "Rent" not in origins:
                        origins.append("Rent")
                        origins = sorted(origins)
                    default_origin_idx = 0
                    if "Savings account Partner 2" in origins:
                        default_origin_idx = origins.index("Savings account Partner 2")
                    origin = st.selectbox("Origin (Account)", origins, index=default_origin_idx, key="form_origin")
                else:
                    origin = st.selectbox("Origin (Account)", ["Savings account Partner 2"], key="form_origin")

                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Submit", type="primary", use_container_width=True, key="submit_btn"):
                        try:
                            if not amount or amount <= 0:
                                st.error("Please enter a valid amount.")
                            elif not type_of_expense or not transaction_category or not distribution or not origin:
                                st.error("Please fill in all required fields.")
                            else:
                                date_str = transaction_date.strftime("%m/%d/%Y")
                                year = transaction_date.year
                                month_num = transaction_date.month
                                month_name = transaction_date.strftime("%B")
                                month_calculated = f"{year}-{month_num:02d}-{month_name}"

                                ws = get_worksheet(SHEET_URL, None, "Table 1")
                                if ws is None:
                                    st.error("Could not access worksheet for writing. Check service account permissions.")
                                else:
                                    amount_formatted = f"{int(amount):,}" if amount > 0 else ""
                                    new_row = [
                                        event_type,
                                        date_str,
                                        month_calculated,
                                        type_of_expense,
                                        transaction_category,
                                        amount_formatted,
                                        distribution,
                                        details if details else "",
                                        origin,
                                    ]
                                    ws.append_row(new_row)
                                    st.cache_data.clear()
                                    st.session_state.show_add_form = False
                                    st.success("✅ Transaction added successfully!")
                                    st.rerun()
                        except Exception as e:
                            st.error(f"Error adding transaction: {str(e)}")

                with col2:
                    if st.button("❌ Cancel", use_container_width=True, key="cancel_btn"):
                        st.session_state.show_add_form = False
                        st.rerun()

        st.markdown("---")

    # Build filter options from main table
    months = ["All"] + sorted(df_main["month"].dropna().unique().tolist()) if "month" in df_main.columns else ["All"]

    # Extract years from months for annual filter
    years = ["All"]
    if "month" in df_main.columns:
        year_set = set()
        for m in df_main["month"].dropna().unique():
            try:
                year = m.split("-")[0]
                year_set.add(year)
            except Exception:
                pass
        years = ["All"] + sorted(list(year_set))

    categories = ["All"] + sorted(df_main["transaction_category"].dropna().unique().tolist()) if "transaction_category" in df_main.columns else ["All"]
    distributions = ["All"] + sorted(df_main["distribution"].dropna().unique().tolist()) if "distribution" in df_main.columns else ["All"]
    origins_list = ["All"] + sorted(df_main["origin"].dropna().unique().tolist()) if "origin" in df_main.columns else ["All"]
    types = ["All"] + sorted(df_main["type_of_expense"].dropna().unique().tolist()) if "type_of_expense" in df_main.columns else ["All"]

    default_month_idx = 0
    if len(months) > 1:
        default_month_idx = len(months) - 1

    with st.sidebar:
        st.markdown("### 📅 Period Filter")
        period_type = st.radio("View by:", ["Monthly", "Annual"], horizontal=True)

        if period_type == "Annual":
            year_filter = st.selectbox("Year", years, index=len(years) - 1 if len(years) > 1 else 0)

            if year_filter != "All":
                year_months = [m for m in sorted(df_main["month"].dropna().unique().tolist()) if m.startswith(year_filter)]
                selected_months = st.multiselect(
                    "Select months to include",
                    options=year_months,
                    default=year_months,
                    help="Select which months from the year to include in the analysis",
                )
                if not selected_months:
                    month = "All"
                elif len(selected_months) == len(year_months):
                    month = "All"
                else:
                    month = selected_months
            else:
                available_years = [y for y in years if y != "All"]
                selected_years = st.multiselect(
                    "Select years to include",
                    options=available_years,
                    default=available_years,
                    help="Select which years to include in the analysis",
                )
                if not selected_years:
                    month = "All"
                elif len(selected_years) == len(available_years):
                    month = "All"
                else:
                    selected_year_months = []
                    for yr in selected_years:
                        selected_year_months.extend([m for m in df_main["month"].dropna().unique() if m.startswith(yr)])
                    month = selected_year_months if selected_year_months else "All"
        else:
            month = st.selectbox("Month", months, index=default_month_idx)

        st.markdown("---")
        category = st.selectbox("Category", categories)
        distribution = st.selectbox("Distribution", distributions)
        origin_filter = st.selectbox("Origin (account)", origins_list)
        event_filter = st.selectbox("Event type", ["All", "Expense", "Income"], index=1)
        type_filter = st.selectbox("Type of expense", types)

    df_filtered = apply_filters(df_main, month, category, distribution, origin_filter, event_filter, type_filter)

    if df_filtered.empty:
        st.warning("No data for the selected filters.")
        return

    # Calculate income/expense from month-filtered data
    df_for_totals = apply_filters(df_main, month, category, distribution, origin_filter, "All", type_filter)
    expenses = df_filtered[df_filtered["is_expense"]]
    incomes_for_totals = df_for_totals[df_for_totals["is_income"]]
    expenses_for_totals = df_for_totals[df_for_totals["is_expense"]]
    total_expenses = expenses_for_totals["amount"].sum()
    total_income = incomes_for_totals["amount"].sum()
    net = total_income - total_expenses

    # Household Income Breakdown
    st.subheader("👥 Household Income & Budget Overview")
    if not incomes_for_totals.empty and "distribution" in incomes_for_totals.columns:
        income_by_person = incomes_for_totals.groupby("distribution")["amount"].sum().sort_values(ascending=False)
        num_people = len(income_by_person)
        income_cols = st.columns(num_people + 1)

        for idx, (person, income_amt) in enumerate(income_by_person.items()):
            with income_cols[idx]:
                pct = (income_amt / total_income * 100) if total_income > 0 else 0
                st.metric(f"💰 {person}'s Income", money(income_amt), delta=f"{pct:.1f}% of household")

        with income_cols[-1]:
            st.metric("🏠 Household Total", money(total_income), delta="100%")
    else:
        st.info("No income data available for breakdown.")

    st.markdown("---")

    # Top metrics row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Income", money(total_income))
    c2.metric("Total Expenses", money(total_expenses))
    c3.metric("Net", money(net), delta=f"{net / (total_income or 1):.1%}" if total_income else None)
    c4.metric("Transactions", len(df_filtered))

    st.markdown("---")

    # Debt Sankey Diagram
    st.subheader("💸 Debt Distribution (18 Cases)")
    st.caption("Expense flow & who owes what (Distribution × Origin)")

    try:
        from chart_utils import create_debt_sankey

        debt_sankey_fig = create_debt_sankey(expenses)

        if debt_sankey_fig:
            st.plotly_chart(debt_sankey_fig, use_container_width=True)

            with st.expander("ℹ️ How it Works", expanded=False):
                st.markdown("""
                ### 18 Cases Analysis
                
                All combinations of **Distribution** (50/50, Partner 1, Partner 2) × **Origin** (Rent, Savings P1, Savings P2) × **Type** (Fixed, One-time) = **18 cases**.
                
                #### Flow:
                - **Left (Green)**: Nothing Owed - expenses where distribution matches origin
                - **Center (Gray)**: TOTAL - all expenses
                - **Right (Pink/Blue)**: Debts owed by Partner 2 and Partner 1
                - **Far Right**: Final totals owed
                
                #### Logic:
                
                **Nothing Owed (6 cases):**
                - 50/50 from Rent ✓
                - Partner 1 from Partner 1's savings ✓
                - Partner 2 from Partner 2's savings ✓
                
                **Partner 2 Owes:**
                - Cases 2, 7, 11, 16: 50% share
                - Cases 8, 17: 100% of amount
                
                **Partner 1 Owes:**
                - Cases 3, 4, 12, 13: 50% share
                - Cases 6, 15: 100% of amount
                """)
        else:
            st.info("No data available for debt analysis in the selected period.")
    except Exception as e:
        st.error(f"Error generating debt Sankey: {e}")

    st.markdown("---")

    # Charts row 1: Income vs Expense over time, by category
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📆 Income vs Expense over time")
        if "date_parsed" in df_filtered.columns:
            timeline = (
                df_filtered.groupby([df_filtered["date_parsed"].dt.date, "event_lower"])["amount"]
                .sum()
                .reset_index()
            )
            timeline.columns = ["date", "event", "amount"]
            fig = px.bar(
                timeline,
                x="date",
                y="amount",
                color="event",
                barmode="group",
                labels={"amount": "Amount (COP)", "date": "Date", "event": "Type"},
                color_discrete_map={"income": "#2ecc71", "expense": "#e74c3c"},
            )
            fig.update_layout(
                template="plotly_dark",
                font_color="#e8e8e8",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8"),
                legend=dict(font_color="#e8e8e8"),
                height=350,
                hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial", font_color="#000000"),
            )
            fig.update_traces(
                text=[f"${y:,.0f}" for y in timeline["amount"]],
                textposition="outside",
                textfont=dict(color="#ffffff", size=12, family="Arial Black"),
                hovertemplate="<b>%{x}</b><br>Amount: $%{y:,.0f} COP<extra></extra>",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No date data available.")

    with col2:
        st.subheader("📊 Expenses by category")
        if not expenses.empty and "transaction_category" in expenses.columns:
            cat_sum = expenses.groupby("transaction_category")["amount"].sum().sort_values(ascending=False)
            fig = px.pie(values=cat_sum.values, names=cat_sum.index, title="Category share")
            fig.update_layout(
                template="plotly_dark",
                font=dict(color="#000000", size=14),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=450,
                showlegend=True,
                legend=dict(
                    font=dict(color="#000000", size=13, family="Arial"),
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor="#000000",
                    borderwidth=2,
                ),
                hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial", font_color="#000000"),
            )
            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
                textfont=dict(color="#1a1a2e", size=12),
                hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.0f} COP<br>Percentage: %{percent}<extra></extra>",
                marker=dict(line=dict(color="#1a1a2e", width=2)),
                hole=0.0,
                pull=[0.05] * len(cat_sum),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense category data.")

    # Charts row 2: Distribution, Origin, and Monthly in 3-column layout
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("👥 Distribution (who pays)")
        if "distribution" in expenses.columns and not expenses.empty:
            dist_sum = expenses.groupby("distribution")["amount"].sum().sort_values(ascending=False)
            fig = px.bar(
                x=dist_sum.index,
                y=dist_sum.values,
                labels={"x": "Distribution", "y": "Amount (COP)"},
                title="Expenses by distribution",
                text=[f"${y:,.0f}" for y in dist_sum.values],
            )
            fig.update_layout(
                template="plotly_dark",
                font_color="#e8e8e8",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8"),
                height=300,
                hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial", font_color="#000000"),
            )
            fig.update_traces(
                textposition="outside",
                textfont=dict(color="#ffffff", size=14, family="Arial Black"),
                hovertemplate="<b>%{x}</b><br>Amount: $%{y:,.0f} COP<extra></extra>",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No distribution data.")

    with col2:
        st.subheader("🏦 Origin (account)")
        if "origin" in expenses.columns and not expenses.empty:
            origin_sum = expenses.groupby("origin")["amount"].sum().sort_values(ascending=False)

            # Calculate projected 50/50 fixed expenses from Table 2 divided by 2
            projected_5050_per_person = 0
            if df_fixed is not None and not df_fixed.empty and "distribution" in df_fixed.columns:
                fixed_5050 = df_fixed[df_fixed["distribution"] == "50/50"]
                if not fixed_5050.empty:
                    total_5050 = fixed_5050["amount"].sum()
                    projected_5050_per_person = total_5050 / 2

            origin_data = origin_sum.to_dict()
            origin_data["Projected 50/50 (÷2)"] = projected_5050_per_person

            fig = px.bar(
                x=list(origin_data.keys()),
                y=list(origin_data.values()),
                labels={"x": "Origin", "y": "Amount (COP)"},
                title="Expenses by origin (includes projected 50/50)",
            )
            fig.update_layout(
                template="plotly_dark",
                font_color="#e8e8e8",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8"),
                height=300,
                hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", font_color="#000000"),
            )
            fig.update_traces(hovertemplate="<b>%{x}</b><br>Amount: $%{y:,.0f} COP<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)

            if projected_5050_per_person > 0:
                st.caption(f"📌 Note: 'Projected 50/50 (÷2)' = ${projected_5050_per_person:,.0f} COP (Total 50/50 fixed expenses from Table 2 divided by 2)")
        else:
            st.info("No origin data.")

    with col3:
        st.subheader("📅 Monthly income vs expense")
        if "month" in df_main.columns:
            df_monthly = apply_filters(df_main, month, "All", "All", "All", "All", "All")
            monthly = df_monthly.groupby(["month", "event_lower"])["amount"].sum().reset_index()
            fig = px.bar(
                monthly,
                x="month",
                y="amount",
                color="event_lower",
                barmode="group",
                labels={"amount": "Amount (COP)", "month": "Month", "event_lower": "Type"},
                color_discrete_map={"income": "#2ecc71", "expense": "#e74c3c"},
            )
            fig.update_layout(
                template="plotly_dark",
                font_color="#e8e8e8",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8", tickangle=45),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8"),
                legend=dict(font_color="#e8e8e8"),
                height=300,
                hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", font_color="#000000"),
            )
            fig.update_traces(hovertemplate="<b>%{x}</b><br>Amount: $%{y:,.0f} COP<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)

    # Fixed expenses section (Table 2)
    st.markdown("---")
    st.subheader("📌 Fixed expenses (Table 2)")
    if df_fixed is not None and not df_fixed.empty:
        fixed_total = df_fixed["amount"].sum()

        # Calculate amounts by origin (savings accounts)
        projected_p1_account = 0
        projected_p2_account = 0
        already_paid_p1_account = 0
        already_paid_p2_account = 0
        one_payment_total = 0

        if "origin" in df_fixed.columns:
            by_origin = df_fixed.groupby("origin")["amount"].sum()
            projected_p1_account = by_origin.get("Savings account Partner 1", 0)
            projected_p2_account = by_origin.get("Savings account Partner 2", 0)

            if "one_payment" in df_fixed.columns:
                one_payment_rows = df_fixed[df_fixed["one_payment"] == True]
                one_payment_total = one_payment_rows["amount"].sum()

            already_paid_p1_5050 = 0
            already_paid_p1_personal = 0
            already_paid_p2_5050 = 0
            already_paid_p2_personal = 0
            rent_account_total = 0

            if df_main is not None and not df_main.empty and "details" in df_main.columns:
                fixed_in_table1 = df_filtered[df_filtered["type_of_expense"] == "Fixed"]

                if not fixed_in_table1.empty and "origin" in fixed_in_table1.columns and "distribution" in fixed_in_table1.columns:
                    for _, row in fixed_in_table1.iterrows():
                        row_origin = row.get("origin", "")
                        row_dist = row.get("distribution", "")
                        row_amount = row.get("amount", 0)

                        if row_origin == "Savings account Partner 1":
                            if row_dist == "50/50":
                                already_paid_p1_5050 += row_amount
                            else:
                                already_paid_p1_personal += row_amount
                        elif row_origin == "Savings account Partner 2":
                            if row_dist == "50/50":
                                already_paid_p2_5050 += row_amount
                            else:
                                already_paid_p2_personal += row_amount

                    already_paid_p1_account = already_paid_p1_5050 + already_paid_p1_personal
                    already_paid_p2_account = already_paid_p2_5050 + already_paid_p2_personal

                rent_transactions = df_filtered[df_filtered["origin"] == "Rent"]
                if not rent_transactions.empty:
                    rent_account_total = rent_transactions["amount"].sum()

                # Cross-account payments
                p2_pays_p1_count = 0
                p2_pays_p1_amount = 0
                p1_pays_p2_count = 0
                p1_pays_p2_amount = 0

                all_expenses = df_filtered[df_filtered["is_expense"]]
                if not all_expenses.empty and "origin" in all_expenses.columns and "distribution" in all_expenses.columns:
                    p2_for_p1 = all_expenses[
                        (all_expenses["origin"] == "Savings account Partner 2") & (all_expenses["distribution"] == "Partner 1")
                    ]
                    if not p2_for_p1.empty:
                        p2_pays_p1_count = len(p2_for_p1)
                        p2_pays_p1_amount = p2_for_p1["amount"].sum()

                    p1_for_p2 = all_expenses[
                        (all_expenses["origin"] == "Savings account Partner 1") & (all_expenses["distribution"] == "Partner 2")
                    ]
                    if not p1_for_p2.empty:
                        p1_pays_p2_count = len(p1_for_p2)
                        p1_pays_p2_amount = p1_for_p2["amount"].sum()

        # Calculate distribution counts (Partner 1 and Partner 2 only, no 50/50)
        p1_count = 0
        p2_count = 0
        p1_amount = 0
        p2_amount = 0

        if "distribution" in df_fixed.columns:
            non_5050 = df_fixed[df_fixed["distribution"].isin(["Partner 1", "Partner 2"])]
            if not non_5050.empty:
                dist_counts = non_5050["distribution"].value_counts()
                dist_amounts = non_5050.groupby("distribution")["amount"].sum()
                p1_count = dist_counts.get("Partner 1", 0)
                p2_count = dist_counts.get("Partner 2", 0)
                p1_amount = dist_amounts.get("Partner 1", 0)
                p2_amount = dist_amounts.get("Partner 2", 0)

        # Three-column layout
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 💳 Projected Payments by Account")
            st.metric(
                "Savings account Partner 1",
                money(projected_p1_account),
                help="Total amount projected to be paid from Partner 1's savings account",
            )
            st.metric(
                "Savings account Partner 2",
                money(projected_p2_account),
                help="Total amount projected to be paid from Partner 2's savings account",
            )
            st.metric("Total Fixed Expenses", money(fixed_total))
            one_payment_pct = (one_payment_total / fixed_total * 100) if fixed_total > 0 else 0
            st.metric(
                "One Payment Total",
                money(one_payment_total),
                delta=f"{one_payment_pct:.1f}% of total",
                help="Total confirmed one-time payments from Table 2 (one_payment=TRUE)",
            )

            st.markdown("---")
            st.markdown("#### ✅ Already Paid by Account")
            st.caption("Calculated from Table 1 transactions")

            st.metric(
                "Already paid (P1 account)",
                money(already_paid_p1_account),
                help="Amount already paid from Partner 1's savings account (from Table 1)",
            )
            if already_paid_p1_account > 0:
                st.caption(f"  • 50/50: {money(already_paid_p1_5050)} | Personal P1: {money(already_paid_p1_personal)}")

            st.metric(
                "Already paid (P2 account)",
                money(already_paid_p2_account),
                help="Amount already paid from Partner 2's savings account (from Table 1)",
            )
            if already_paid_p2_account > 0:
                st.caption(f"  • 50/50: {money(already_paid_p2_5050)} | Personal P2: {money(already_paid_p2_personal)}")

            total_paid = already_paid_p1_account + already_paid_p2_account
            paid_pct = (total_paid / fixed_total * 100) if fixed_total > 0 else 0
            st.metric("Total Already Paid", money(total_paid), delta=f"{paid_pct:.1f}%")

        with col2:
            st.markdown("#### 👤 Distribution (Partner 1 & Partner 2 only)")
            st.caption("Excluding 50/50 shared expenses")
            st.metric(
                "Partner 1 expenses",
                f"{p1_count} items",
                delta=money(p1_amount),
                help="Number of fixed expenses assigned to Partner 1 only",
            )
            st.metric(
                "Partner 2 expenses",
                f"{p2_count} items",
                delta=money(p2_amount),
                help="Number of fixed expenses assigned to Partner 2 only",
            )

            total_personal = p1_amount + p2_amount
            if total_personal > 0:
                p1_pct = p1_amount / total_personal * 100
                p2_pct = p2_amount / total_personal * 100
                st.metric(
                    "P1/P2 Ratio",
                    f"{p1_pct:.1f}% / {p2_pct:.1f}%",
                    help="Expense ratio between Partner 1 and Partner 2 for non-50/50 fixed expenses",
                )

            st.markdown("---")
            st.markdown("#### 🔄 Cross-Account Payments")
            st.caption("When one account pays for the other's expenses")
            st.metric(
                "P2 → P1",
                f"{p2_pays_p1_count} items",
                delta=money(p2_pays_p1_amount),
                help="Partner 2's account paying for Partner 1's personal expenses",
            )
            st.metric(
                "P1 → P2",
                f"{p1_pays_p2_count} items",
                delta=money(p1_pays_p2_amount),
                help="Partner 1's account paying for Partner 2's personal expenses",
            )

            st.markdown("---")
            st.markdown("#### 🏠 Rent Account Tracker")
            st.caption("All transactions from Rent origin")
            st.metric(
                "Rent Account Total",
                money(rent_account_total),
                help="Total amount from Rent account (all expense types from Table 1)",
            )

        with col3:
            st.markdown("#### 📊 Fixed Expenses by Category")
            if "transaction_category" in df_fixed.columns:
                fixed_cat = df_fixed.groupby("transaction_category")["amount"].sum().sort_values(ascending=False)
                fig = px.bar(
                    x=fixed_cat.index,
                    y=fixed_cat.values,
                    labels={"x": "Category", "y": "Amount (COP)"},
                )
                fig.update_layout(
                    template="plotly_dark",
                    font_color="#e8e8e8",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8", tickangle=45),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8"),
                    height=500,
                    showlegend=False,
                    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", font_color="#000000"),
                )
                fig.update_traces(
                    marker_color="rgba(59, 130, 246, 0.8)",
                    hovertemplate="<b>%{x}</b><br>Amount: $%{y:,.0f} COP<extra></extra>",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No category data for fixed expenses.")

        # Two-column layout for expense charts
        st.markdown("#### 📊 Expense Tracking")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("**Fixed Expenses: Expected vs Already Paid**")
            if "amount_paid%" in df_fixed.columns and "details" in df_fixed.columns:
                chart_data = []
                for _, row in df_fixed.iterrows():
                    expense_name = row.get("details", "Unknown")
                    expected_amount = row.get("amount", 0)
                    paid_percentage = row.get("amount_paid%", 0)
                    paid_amount = expected_amount * (paid_percentage / 100) if paid_percentage > 0 else 0

                    chart_data.append({"Expense": expense_name, "Type": "Expected", "Amount": expected_amount})
                    chart_data.append({"Expense": expense_name, "Type": "Already Paid", "Amount": paid_amount})

                df_chart = pd.DataFrame(chart_data)

                fig = go.Figure()
                expected_data = df_chart[df_chart["Type"] == "Expected"].sort_values("Amount", ascending=True)
                fig.add_trace(
                    go.Bar(
                        y=expected_data["Expense"],
                        x=expected_data["Amount"],
                        name="Expected",
                        orientation="h",
                        marker=dict(color="rgba(59, 130, 246, 0.6)"),
                        text=expected_data["Amount"].apply(lambda x: f"${x:,.0f}"),
                        textposition="outside",
                        textfont=dict(color="#ffffff", size=16, family="Arial Black"),
                    )
                )

                paid_data = df_chart[df_chart["Type"] == "Already Paid"].sort_values("Amount", ascending=True)
                fig.add_trace(
                    go.Bar(
                        y=paid_data["Expense"],
                        x=paid_data["Amount"],
                        name="Already Paid",
                        orientation="h",
                        marker=dict(color="rgba(46, 204, 113, 0.8)"),
                        text=paid_data["Amount"].apply(lambda x: f"${x:,.0f}" if x > 0 else ""),
                        textposition="inside",
                        textfont=dict(color="#ffffff", size=32, family="Arial Black"),
                    )
                )

                fig.update_layout(
                    barmode="group",
                    template="plotly_dark",
                    font_color="#1a1a2e",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(title="Amount (COP)", gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8"),
                    yaxis=dict(title="", gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8", tickfont=dict(color="#ffffff", size=14, family="Arial Black")),
                    legend=dict(font_color="#e8e8e8", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    height=max(600, len(df_fixed) * 40),
                    showlegend=True,
                    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", font_color="#000000"),
                )
                fig.update_traces(hovertemplate="<b>%{y}</b><br>Amount: $%{x:,.0f} COP<extra></extra>")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Payment tracking data not available.")

        with chart_col2:
            st.markdown("**One-Time Expenses**")
            one_time_expenses = df_filtered[df_filtered["type_of_expense"] == "One time"]

            if not one_time_expenses.empty and "details" in one_time_expenses.columns:
                one_time_summary = one_time_expenses.groupby("details")["amount"].sum().sort_values(ascending=True)

                if not one_time_summary.empty:
                    fig = go.Figure()
                    fig.add_trace(
                        go.Bar(
                            y=one_time_summary.index,
                            x=one_time_summary.values,
                            orientation="h",
                            marker=dict(color="rgba(255, 159, 64, 0.8)"),
                            text=[f"${x:,.0f}" for x in one_time_summary.values],
                            textposition="outside",
                            textfont=dict(color="#ffffff", size=16, family="Arial Black"),
                        )
                    )

                    fig.update_layout(
                        template="plotly_dark",
                        font_color="#e8e8e8",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(title="Amount (COP)", gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8"),
                        yaxis=dict(title="", gridcolor="rgba(255,255,255,0.1)", title_font_color="#e8e8e8"),
                        height=max(600, len(one_time_summary) * 40),
                        showlegend=False,
                        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", font_color="#000000"),
                    )
                    fig.update_traces(hovertemplate="<b>%{y}</b><br>Amount: $%{x:,.0f} COP<extra></extra>")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No one-time expenses in the selected period.")
            else:
                st.info("No one-time expenses in the selected period.")

        st.markdown("#### Fixed expenses table with budgeting details")
        disp_cols = [
            "details",
            "transaction_category",
            "amount",
            "distribution",
            "origin",
            "amount_paid%",
            "one_payment",
            "months_valid",
        ]
        show_cols = [c for c in disp_cols if c in df_fixed.columns]
        df_show = df_fixed[show_cols].copy()
        if "amount" in df_show.columns:
            df_show["amount"] = df_show["amount"].apply(money)
        if "amount_paid%" in df_show.columns:
            df_show["amount_paid%"] = df_show["amount_paid%"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) and x != 0 else "0%")

        st.dataframe(
            df_show,
            use_container_width=True,
            hide_index=True,
            height=400,
            column_config={
                "details": st.column_config.TextColumn("Expense", width="medium"),
                "transaction_category": st.column_config.TextColumn("Category", width="medium"),
                "amount": st.column_config.TextColumn("Amount", width="small"),
                "distribution": st.column_config.TextColumn("Who Pays", width="small"),
                "origin": st.column_config.TextColumn("Account", width="medium"),
                "amount_paid%": st.column_config.TextColumn("% Paid", width="small"),
                "one_payment": st.column_config.CheckboxColumn("One Payment", width="small"),
                "months_valid": st.column_config.NumberColumn("Months Valid", width="small"),
            },
        )
    else:
        st.info("No fixed expenses data found in 'Table 2 Fixed expenses'.")

    # Detailed table for filtered data
    st.markdown("---")
    st.subheader("📋 Transactions (filtered)")
    display_cols = [
        "event",
        "date",
        "month",
        "type_of_expense",
        "transaction_category",
        "amount",
        "distribution",
        "details",
        "origin",
    ]
    cols = [c for c in display_cols if c in df_filtered.columns]
    df_table = df_filtered[cols].copy()
    if "amount" in df_table.columns:
        df_table["amount"] = df_table["amount"].apply(money)
    st.dataframe(df_table, use_container_width=True, hide_index=True, height=400)

    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Download filtered CSV",
        data=csv,
        file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
