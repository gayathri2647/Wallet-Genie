import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import random

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username

# Check authentication
check_auth()

# Page config
st.set_page_config(
    page_title="Smart Sync - WalletGenie",
    page_icon="🔄",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .sync-status {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    .synced {
        background-color: #90EE90;
    }
    .not-synced {
        background-color: #FFB6C1;
    }
    .sync-info {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Smart Sync 🔄")
st.write("Keep your transactions automatically synchronized")

# Smart Sync toggle
sync_enabled = st.toggle("Enable Smart Sync", value=True)

if sync_enabled:
    # Mock sync status
    last_sync = datetime.now() - timedelta(minutes=random.randint(5, 60))
    sync_status = random.choice(["Synced", "Not Synced"])
    
    # Display sync status
    status_class = "synced" if sync_status == "Synced" else "not-synced"
    st.markdown(f"""
        <div class="sync-status {status_class}">
            <h2>{sync_status}</h2>
            <p>Last sync: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sync information
    st.subheader("Sync Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="sync-info">
                <h4>Connected Accounts</h4>
                ✅ Main Bank Account<br>
                ✅ Credit Card<br>
                ✅ Investment Account<br>
                ❌ Crypto Wallet (Click to connect)
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="sync-info">
                <h4>Sync Statistics</h4>
                🔄 Total syncs today: 24<br>
                📊 Success rate: 98%<br>
                ⚡ Average sync time: 2.3s<br>
                📱 Last device: Web
            </div>
        """, unsafe_allow_html=True)
    
    # Auto-updating chart preview
    st.subheader("Live Transaction Preview")
    
    # Generate mock real-time data
    times = [(datetime.now() - timedelta(hours=x)) for x in range(24, 0, -1)]
    amounts = [random.uniform(50, 200) for _ in range(24)]
    df = pd.DataFrame({
        'Time': times,
        'Amount': amounts
    })
    
    fig = px.line(
        df,
        x='Time',
        y='Amount',
        title='24-Hour Transaction Activity',
        markers=True
    )
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Transaction Amount ($)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Sync settings
    st.subheader("Sync Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox(
            "Sync Frequency",
            ["Every 15 minutes", "Every 30 minutes", "Every hour", "Every 4 hours", "Daily"]
        )
        st.checkbox("Notify on sync failure", value=True)
    
    with col2:
        st.multiselect(
            "Sync Categories",
            ["Transactions", "Account Balance", "Bills", "Investments"],
            default=["Transactions", "Account Balance"]
        )
        st.checkbox("Auto-categorize new transactions", value=True)
    
else:
    st.warning("""
        ⚠️ Smart Sync is disabled. Enable it to:
        - Automatically sync your transactions
        - Get real-time balance updates
        - Receive smart notifications
        - Keep your data up-to-date across devices
    """)

# Manual sync button
if st.button("Sync Now", disabled=not sync_enabled):
    with st.spinner("Syncing..."):
        # Simulate sync delay
        import time
        time.sleep(2)
    st.success("✅ Sync completed successfully!")

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))