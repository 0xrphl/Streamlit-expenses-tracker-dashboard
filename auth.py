import streamlit as st
from config import get_app_password


def check_auth():
    """Check if user is authenticated. Returns True if authenticated."""
    app_password = get_app_password()

    # Check query parameters first (persists across refreshes)
    query_params = st.query_params
    if "auth" in query_params and query_params["auth"] == app_password:
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = True
        return True

    # Check session state
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
        passkey = st.text_input(
            "Passkey",
            type="password",
            label_visibility="collapsed",
            placeholder="Enter passkey",
        )

        if st.button("Login", type="primary", use_container_width=True):
            if passkey == app_password:
                st.session_state.authenticated = True
                # Set query parameter to persist across refreshes
                st.query_params["auth"] = app_password
                st.rerun()
            else:
                st.error("❌ Incorrect passkey. Please try again.")

        st.markdown("---")
        st.caption("Enter the passkey to access the dashboard")


def logout():
    """Log out the user."""
    st.session_state.authenticated = False
    st.query_params.clear()
    st.rerun()
