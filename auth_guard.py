import streamlit as st

def check_auth():
    """
    Check if user is authenticated. If not, show warning and stop app.
    To be used at the start of each protected page.
    """
    if not st.session_state.get('logged_in', False):
        st.warning('⚠️ You need to login first.')
        st.stop()
        return False
    return True

def get_username():
    """Get the display name of the logged-in user, falling back to email prefix or 'Guest'."""
    if st.session_state.get('username'):
        return st.session_state.username
    elif st.session_state.get('email'):
        return st.session_state.email.split('@')[0]
    return 'Guest' # Fallback if no username or email is available