import streamlit as st
import pandas as pd
import sys
import os
import firebase_admin
from firebase_admin import firestore
from datetime import datetime

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from firebase_init import init_firestore
from config import CURRENCY # Assuming CURRENCY is defined in config.py

# Check authentication
check_auth()

# Initialize Firebase DB client
db = init_firestore()

# --- IMPORTANT: Replace with dynamic user ID ---
user_id = "yugesh_demo_uid"
# --- End of IMPORTANT ---

# Page config
st.set_page_config(
    page_title="Transaction History - WalletGenie",
    page_icon="📜",
    layout="wide"
)

st.title("Transaction History 📜")
st.write("View and manage all your past transactions.")

# Function to get user transactions from Firestore
@st.cache_data(ttl=60) # Cache the data for 60 seconds
def get_user_transactions(uid):
    transactions = []
    # Fetch transactions from the 'transactions' subcollection for the specific user
    tx_ref = db.collection("users").document(uid).collection("transactions").order_by("date", direction=firestore.Query.DESCENDING).stream()
    for tx in tx_ref:
        tx_data = tx.to_dict()
        tx_data['id'] = tx.id # Add document ID for potential future delete/edit
        transactions.append(tx_data)
    return transactions

# Fetch transactions
tx_data = get_user_transactions(user_id)

if tx_data:
    df = pd.DataFrame(tx_data)

    # Convert 'date' column to datetime objects for proper sorting and filtering
    df['date'] = pd.to_datetime(df['date'], errors='coerce', format='%m/%d/%Y')
    df.dropna(subset=['date'], inplace=True) # Remove rows where date conversion failed

    # Sort by date descending by default
    df = df.sort_values(by='date', ascending=False)

    # Display total transactions count
    st.info(f"Total Transactions: **{len(df)}**")

    # Filters
    st.subheader("Filter Transactions")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Filter by type
        transaction_type_filter = st.selectbox("Filter by Type", ["All", "Expense", "Income"])
        if transaction_type_filter != "All":
            df = df[df['type'].str.lower() == transaction_type_filter.lower()]

    with col2:
        # Filter by category (get unique categories from current filtered DataFrame)
        all_categories = df['category'].unique().tolist()
        category_filter = st.selectbox("Filter by Category", ["All"] + sorted(all_categories))
        if category_filter != "All":
            df = df[df['category'] == category_filter]

    with col3:
        # Date range filter
        min_date = df['date'].min().date() if not df.empty else datetime.today().date()
        max_date = df['date'].max().date() if not df.empty else datetime.today().date()
        date_range = st.date_input("Filter by Date Range",
                                  value=(min_date, max_date),
                                  min_value=min_date,
                                  max_value=max_date)

        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
        elif len(date_range) == 1: # Handle case where only one date is selected (e.g., in calendar)
            start_date = date_range[0]
            df = df[df['date'].dt.date == start_date]

    with col4:
        # Search by description
        search_query = st.text_input("Search by Description", "").strip()
        if search_query:
            df = df[df['description'].str.contains(search_query, case=False, na=False)]


    # Display the filtered data using st.dataframe or st.table
    st.subheader("Filtered Transactions")

    # Format amount for display
    df['amount_display'] = df.apply(
        lambda row: f"{CURRENCY} {row['amount']:,.2f}", axis=1
    )
    df['date_display'] = df['date'].dt.strftime('%Y-%m-%d')


    # Select columns to display
    display_cols = ['date_display', 'description', 'category', 'type', 'amount_display']
    display_df = df[display_cols].rename(columns={
        'date_display': 'Date',
        'description': 'Description',
        'category': 'Category',
        'type': 'Type',
        'amount_display': 'Amount'
    })

    if not display_df.empty:
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No transactions match the selected filters.")

    # Option to download filtered data
    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Transactions as CSV",
            data=csv,
            file_name="filtered_transactions.csv",
            mime="text/csv",
        )

else:
    st.info("No transactions recorded yet. Add some transactions using the 'Add Transaction' page!")

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))