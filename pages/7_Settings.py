import streamlit as st
import sys
import os
import firebase_admin 
from firebase_admin import firestore
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from firebase_init import init_firestore
from config import CURRENCY
from shared_utils import get_categories, update_categories_firestore

# Check authentication
check_auth()

# Initialize Firebase
if not firebase_admin._apps:
    try:
        cred = firebase_admin.credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}. Please ensure 'firebase_key.json' is correctly placed and valid.")
        st.stop()

db = firestore.client()

user_id = st.session_state.user_id

# Page config
st.set_page_config(
    page_title="Settings - WalletGenie",
    page_icon="⚙️",
    layout="centered"
)

# Apply custom CSS for modern UI
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton button {
        border-radius: 20px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .settings-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .danger-zone {
        background-color: #fff5f5;
        border: 1px solid #feb2b2;
        border-radius: 10px;
        padding: 20px;
        margin-top: 30px;
    }
    .category-item {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        margin: 5px 0;
        background-color: white;
        border-radius: 5px;
        border: 1px solid #e9ecef;
    }
    .category-name {
        flex-grow: 1;
        color: #333;
    }
    .delete-btn {
        color: #e53e3e;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        background-color: #262730;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4299e1 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Modern header with user info
username = get_username()
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <h1 style="margin: 0;">⚙️ Settings</h1>
    <div style="background-color: #262730; padding: 8px 16px; border-radius: 20px;">
        <span style="font-weight: 500;">👤 {username}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Function to get user transactions (for activity chart)
def get_user_transactions(uid):
    tx_ref = db.collection("users").document(uid).collection("transactions").stream()
    return [tx.to_dict() for tx in tx_ref]

# Create tabs for better organization
#tabs = st.tabs(["🔒 Account"])

# # --- Recent Activity Section ---
# with tabs[0]:
#     with st.container():
#        # st.markdown('<div class="settings-card">', unsafe_allow_html=True)
#         st.subheader("Recent Transaction Activity")
#         st.write("View your recent transaction activity over the last 24 hours.")

#     # Fetch recent transactions for the 24-hour activity chart
#     tx_data = get_user_transactions(user_id)
#     df = pd.DataFrame(tx_data)

#     if not df.empty and 'date' in df.columns and 'amount' in df.columns:
#         df['date'] = pd.to_datetime(df['date'], errors='coerce')
#         df.dropna(subset=['date', 'amount'], inplace=True)

#         # Filter for transactions in the last 24 hours
#         recent_transactions = df[df['date'] >= (datetime.now() - timedelta(days=1))].copy()
#         if not recent_transactions.empty:
#             # Extract hour of day for plotting
#             recent_transactions['hour'] = recent_transactions['date'].dt.hour
#             hourly_activity = recent_transactions.groupby('hour')['amount'].sum().reset_index()
#             # Ensure all hours are present for a smooth chart
#             all_hours = pd.DataFrame({'hour': range(24)})
#             hourly_activity = pd.merge(all_hours, hourly_activity, on='hour', how='left').fillna(0)

#             fig = px.bar(
#                 hourly_activity,
#                 x='hour',
#                 y='amount',
#                 title='Last 24-Hour Transaction Activity',
#                 labels={'hour': 'Hour of Day (24-hour format)', 'amount': f'Transaction Amount ({CURRENCY})'},
#                 color_discrete_sequence=['#4299e1']
#             )
#             fig.update_layout(
#                 xaxis=dict(tickmode='linear', dtick=1),
#                 plot_bgcolor='rgba(0,0,0,0)',
#                 paper_bgcolor='rgba(0,0,0,0)',
#                 margin=dict(l=20, r=20, t=40, b=20),
#                 hoverlabel=dict(bgcolor="white", font_size=12),
#             )
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.info("No transactions recorded in the last 24 hours.")
#     else:
#         st.info("No transaction data available to show activity.")
#     st.markdown('</div>', unsafe_allow_html=True)

# --- Config Categories Section ---
# with tabs[0]:
#     with st.container():
#         #st.markdown('<div class="settings-card">', unsafe_allow_html=True)
#         st.subheader("Configure Transaction Categories")
#         st.write("Manage your custom income and expense categories. You can add up to 20 categories for each type.")

#     MAX_CATEGORIES = 20

#     # Get categories directly from Firestore (no caching)
#     user_categories = get_categories(db, user_id)
#     expense_categories = user_categories.get("expense", [])
#     income_categories = user_categories.get("income", [])

#     # Add New Category
#     with st.expander("➕ Add New Category", expanded=True):
#         with st.form("new_category_form"):
#             col1, col2 = st.columns([3, 1])
#             with col1:
#                 new_category_name = st.text_input("Category Name", placeholder="e.g., Groceries, Freelance Income").strip()
#             with col2:
#                 new_category_type = st.selectbox("Type", ["Expense", "Income"])

#             add_button_disabled = False
#             if new_category_type == "Expense" and len(expense_categories) >= MAX_CATEGORIES:
#                 add_button_disabled = True
#                 st.warning(f"You have reached the maximum of {MAX_CATEGORIES} expense categories.")
#             elif new_category_type == "Income" and len(income_categories) >= MAX_CATEGORIES:
#                 add_button_disabled = True
#                 st.warning(f"You have reached the maximum of {MAX_CATEGORIES} income categories.")

#             submit_add_category = st.form_submit_button(
#                 "Add Category",
#                 disabled=add_button_disabled,
#                 use_container_width=True
#             )

#             if submit_add_category:
#                 if new_category_name:
#                     if new_category_type == "Expense":
#                         if new_category_name not in expense_categories:
#                             expense_categories.append(new_category_name)
#                             update_categories_firestore(db, user_id, {"expense": expense_categories, "income": income_categories})
#                             st.success(f"Category '{new_category_name}' ({new_category_type}) added successfully!")
#                             st.rerun()
#                         else:
#                             st.warning("Category already exists for Expense type.")
#                     else: # Income
#                         if new_category_name not in income_categories:
#                             income_categories.append(new_category_name)
#                             update_categories_firestore(db, user_id, {"expense": expense_categories, "income": income_categories})
#                             st.success(f"Category '{new_category_name}' ({new_category_type}) added successfully!")
#                             st.rerun()
#                         else:
#                             st.warning("Category already exists for Income type.")
#                 else:
#                     st.error("Please enter a category name.")

#     # Display deletion notification if a category was deleted
#     if "deleted_category" in st.session_state:
#         st.success(f"Category '{st.session_state.deleted_category}' has been deleted successfully!")
#         # Clear the notification after displaying it once
#         del st.session_state.deleted_category

#     # Manage Categories
#     category_tabs = st.tabs(["💸 Expense Categories", "💰 Income Categories"])
    
#     with category_tabs[0]:
#         if expense_categories:
#             for i, cat in enumerate(expense_categories):
#                 st.markdown(f"""
#                 <div class="category-item">
#                     <div class="category-name" style="color: #333;">• {cat}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
#                 if st.button("Delete", key=f"del_exp_{i}", help=f"Delete {cat} category"):
#                     if "deleted_category" not in st.session_state:
#                         st.session_state.deleted_category = cat
#                         expense_categories.remove(cat)
#                         update_categories_firestore(db, user_id, {"expense": expense_categories, "income": income_categories})
#                         st.rerun()
#         else:
#             st.info("No custom expense categories defined yet.")

#     with category_tabs[1]:
#         if income_categories:
#             for i, cat in enumerate(income_categories):
#                 st.markdown(f"""
#                 <div class="category-item">
#                     <div class="category-name" style="color: #333;">• {cat}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
#                 if st.button("Delete", key=f"del_inc_{i}", help=f"Delete {cat} category"):
#                     if "deleted_category" not in st.session_state:
#                         st.session_state.deleted_category = cat
#                         income_categories.remove(cat)
#                         update_categories_firestore(db, user_id, {"expense": expense_categories, "income": income_categories})
#                         st.rerun()
#         else:
#             st.info("No custom income categories defined yet.")
#     # st.markdown('</div>', unsafe_allow_html=True)

# --- Account Section ---
# with tabs[0]:
with st.container():
    # st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.subheader("Account Settings")

# Logout button with better styling
if st.button("🚪 Logout", use_container_width=True):
    st.session_state.update({"logged_in": False})
    st.rerun()

# Danger Zone
# st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
st.subheader("⚠️ Danger Zone")

# Delete All Transactions
with st.expander("Delete All Transactions"):
    st.warning("This action cannot be undone. All your transaction data will be permanently deleted.")
    
    # GitHub-style confirmation
    confirmation_text = f"delete-all-transactions-{user_id[:5]}"
    user_confirmation = st.text_input(
        f"To confirm, type '{confirmation_text}' below:",
        key="delete_confirmation"
    )
    
    if st.button("Delete All Transactions", type="primary", use_container_width=True):
        if user_confirmation == confirmation_text:
            # Use the shared utility function to delete all transactions
            from shared_utils import delete_all_transactions
            success = delete_all_transactions(db, user_id)
            
            if success:
                st.success("All transactions have been deleted successfully!")
                st.balloons()
        else:
            st.error("Confirmation text doesn't match. Transactions were not deleted.")

# Delete Account
with st.expander("Delete Account"):
    st.error("⚠️ This action is permanent and cannot be undone. Your account and all associated data will be permanently deleted.")
    
    # GitHub-style confirmation for account deletion
    account_confirmation_text = f"delete-my-account-{user_id[:5]}"
    account_user_confirmation = st.text_input(
        f"To confirm account deletion, type '{account_confirmation_text}' below:",
        key="delete_account_confirmation"
    )
    
    # Second verification with checkbox
    verify_checkbox = st.checkbox("I understand this will permanently delete my account and all my data")
    
    if st.button("Delete My Account", type="primary", use_container_width=True):
        if account_user_confirmation == account_confirmation_text and verify_checkbox:
            # Function to delete user account
            def delete_user_account(db, user_id):
                try:
                    # 1. Delete all transactions
                    from shared_utils import delete_all_transactions
                    delete_all_transactions(db, user_id)
                    
                    # 2. Delete user categories
                    db.collection("users").document(user_id).collection("categories").document("user_categories").delete()
                    
                    # 3. Delete user document
                    db.collection("users").document(user_id).delete()
                    
                    return True
                except Exception as e:
                    st.error(f"Error deleting account: {e}")
                    return False
            
            success = delete_user_account(db, user_id)
            
            if success:
                st.success("Your account has been permanently deleted.")
                st.session_state.update({"logged_in": False})
                st.rerun()
        else:
            if not verify_checkbox:
                st.error("Please check the verification box to confirm.")
            else:
                st.error("Confirmation text doesn't match. Account was not deleted.")

   # st.markdown('</div>', unsafe_allow_html=True)
   #  st.markdown('</div>', unsafe_allow_html=True)