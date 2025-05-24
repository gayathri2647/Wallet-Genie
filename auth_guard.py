import streamlit as st

def check_auth():
    """
    Check if user is authenticated. If not, show warning and return False.
    To be used at the start of each protected page.
    """
    if not st.session_state.get('logged_in', False):
        st.warning('⚠️ You need to login first.')
        st.stop()
        return False
    return True

def get_username():
    """Get the username (email) of the logged-in user"""
    return st.session_state.get('email', 'User')