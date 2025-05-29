import streamlit as st
import sys
import os
import firebase_admin
from firebase_admin import firestore

# Add the root directory to the path for imports to find auth_guard and firebase_init
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from firebase_init import init_firestore

# Check authentication to ensure the user is logged in
check_auth()

# Initialize Firestore DB client
db = init_firestore()

# --- IMPORTANT: Replace with dynamic user ID ---
# In a real application, get the actual user ID from your authentication system
# For demonstration, we'll use a placeholder.
user_id = "yugesh_demo_uid"
# --- End of IMPORTANT ---

# Configure the Streamlit page
st.set_page_config(
    page_title="Config Categories - WalletGenie",
    page_icon="⚙️",
    layout="centered"
)

st.title("Configure Transaction Categories ⚙️")
st.write("Manage your custom income and expense categories. You can add up to 10 categories for each type.")

MAX_CATEGORIES = 10 # Maximum number of categories allowed for each type (expense/income)

# Function to fetch categories from Firestore.
# @st.cache_data is used to cache the results for 60 seconds, reducing Firestore reads.
@st.cache_data(ttl=60)
def get_categories(uid):
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()
    if doc.exists:
        # If the user document exists, retrieve the 'categories' map, defaulting to empty lists if not present
        data = doc.to_dict()
        return data.get("categories", {"expense": [], "income": []})
    # If the user document doesn't exist, return empty lists for categories
    return {"expense": [], "income": []}

# Function to update categories in Firestore.
# Categories are stored in a 'categories' map within the user's document.
def update_categories_firestore(uid, categories_data):
    doc_ref = db.collection("users").document(uid)
    # merge=True ensures other fields in the user's document are preserved
    doc_ref.set({"categories": categories_data}, merge=True)

# Fetch current categories for the logged-in user
user_categories = get_categories(user_id)
expense_categories = user_categories.get("expense", [])
income_categories = user_categories.get("income", [])

st.subheader("Existing Expense Categories")
if expense_categories:
    for cat in expense_categories:
        st.info(f"• {cat}") # Display each expense category
else:
    st.info("No custom expense categories defined yet. Add some below!")

st.subheader("Existing Income Categories")
if income_categories:
    for cat in income_categories:
        st.info(f"• {cat}") # Display each income category
else:
    st.info("No custom income categories defined yet. Add some below!")

st.subheader("Add New Category")

# Form for adding new categories
with st.form("new_category_form"):
    new_category_name = st.text_input("Category Name", placeholder="e.g., Groceries, Freelance Income").strip()
    new_category_type = st.selectbox("Category Type", ["Expense", "Income"])

    # Determine if the 'Add Category' button should be disabled based on the MAX_CATEGORIES limit
    add_button_disabled = False
    if new_category_type == "Expense" and len(expense_categories) >= MAX_CATEGORIES:
        add_button_disabled = True
        st.warning(f"You have reached the maximum of {MAX_CATEGORIES} expense categories. To add more, please remove existing ones directly from Firestore or implement a delete feature.")
    elif new_category_type == "Income" and len(income_categories) >= MAX_CATEGORIES:
        add_button_disabled = True
        st.warning(f"You have reached the maximum of {MAX_CATEGORIES} income categories. To add more, please remove existing ones directly from Firestore or implement a delete feature.")

    submit_add_category = st.form_submit_button(
        "Add Category",
        disabled=add_button_disabled # Disable button if limit is reached
    )

    if submit_add_category:
        if new_category_name:
            if new_category_type == "Expense":
                if new_category_name not in expense_categories:
                    expense_categories.append(new_category_name)
                    # Update Firestore with the new list of expense categories
                    update_categories_firestore(user_id, {"expense": expense_categories, "income": income_categories})
                    st.success(f"Category '{new_category_name}' ({new_category_type}) added successfully!")
                    st.rerun() # Rerun the app to refresh the displayed categories
                else:
                    st.warning("Category already exists for Expense type.")
            else: # Income
                if new_category_name not in income_categories:
                    income_categories.append(new_category_name)
                    # Update Firestore with the new list of income categories
                    update_categories_firestore(user_id, {"expense": expense_categories, "income": income_categories})
                    st.success(f"Category '{new_category_name}' ({new_category_type}) added successfully!")
                    st.rerun() # Rerun the app to refresh the displayed categories
                else:
                    st.warning("Category already exists for Income type.")
        else:
            st.error("Please enter a category name.")

# Logout button in the sidebar
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))