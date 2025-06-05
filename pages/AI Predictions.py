import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Add the root directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_guard import check_auth, get_username
from firebase_init import init_firestore

# Check authentication
check_auth()

# Initialize Firestore
db = init_firestore()
user_id = st.session_state.user_id

# Page config
st.set_page_config(
    page_title="AI Predictions - WalletGenie",
    page_icon="🔮",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .risk-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    .risk-safe {
        background-color: #90EE90;
    }
    .risk-medium {
        background-color: #FFD700;
    }
    .risk-high {
        background-color: #FFB6C1;
    }
    .model-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("AI Predictions 🔮")
st.write("Let's peek into your financial future with machine learning!")

# Function to load transaction data
@st.cache_data(ttl=300)
def load_transaction_data():
    """Load transaction data from Firestore"""
    try:
        # Get data from Firestore
        transactions = []
        # Fetch transactions from the 'transactions' subcollection for the specific user
        tx_ref = db.collection("users").document(user_id).collection("transactions").stream()
        for tx in tx_ref:
            tx_data = tx.to_dict()
            tx_data['id'] = tx.id
            transactions.append(tx_data)
        
        if transactions:
            df = pd.DataFrame(transactions)
            # Ensure date is in datetime format
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df.dropna(subset=['date'], inplace=True)  # Remove rows where date conversion failed
            return df
        
        # If no transactions found, generate sample data
        st.info("No transactions found. Using sample data for demonstration.")
        return generate_sample_data()
    except Exception as e:
        st.warning(f"Error loading transaction data: {e}. Using sample data instead.")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample transaction data for demonstration"""
    dates = pd.date_range(start=datetime.now() - timedelta(days=90), end=datetime.now(), freq='D')
    np.random.seed(42)
    
    # Generate sample transactions
    data = []
    for date in dates:
        # Add income entries
        if date.day == 1 or date.day == 15:  # Salary days
            data.append({
                'description': 'Monthly salary',
                'amount': np.random.normal(5000, 200),
                'date': date,
                'type': 'income',
                'category': 'Salary'
            })
        
        # Add random expenses
        n_expenses = np.random.randint(0, 3)  # 0-2 expenses per day
        for _ in range(n_expenses):
            categories = ['Groceries', 'Dining Out', 'Entertainment', 'Transportation', 'Shopping', 'Utilities', 'Rent']
            category = np.random.choice(categories)
            
            # Different expense ranges based on category
            if category == 'Groceries':
                amount = np.random.normal(100, 30)
            elif category == 'Utilities':
                amount = np.random.normal(150, 20)
            elif category == 'Rent':
                amount = np.random.normal(1500, 100)
            else:
                amount = np.random.normal(50, 25)
                
            data.append({
                'description': f'{category} expense',
                'amount': amount,
                'date': date,
                'type': 'expense',
                'category': category
            })
    
    return pd.DataFrame(data)

# Load data
df = load_transaction_data()

# model selection
st.header("AI Model Selection")
selected_model = st.selectbox(
    "Choose Prediction Model",
    ["Income/Expense Prediction", "Anomaly Detection", "Spending Behavior Clustering", "Future Expense Prediction"]
)

# Prepare data for models
if not df.empty:
    # Ensure date is datetime
    if 'date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # Create features for time series
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_month'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    
    # Separate income and expenses
    income_df = df[df['type'] == 'income'].copy()
    expense_df = df[df['type'] == 'expense'].copy()
    
    # Aggregate by date for time series
    daily_expenses = expense_df.groupby(expense_df['date'].dt.date)['amount'].sum().reset_index()
    daily_income = income_df.groupby(income_df['date'].dt.date)['amount'].sum().reset_index()

    # Income/Expense Prediction Model
    if selected_model == "Income/Expense Prediction":
        st.header("Income & Expense Prediction")
        # st.markdown('<div class="model-card">', unsafe_allow_html=True)
        
        # Forecast duration toggle
        duration = st.radio(
            "Forecast Duration",
            ["7 Days", "30 Days"],
            horizontal=True
        )
        days = 30 if duration == "30 Days" else 7
        
        # Check if we have enough data
        if len(expense_df) > 0:
            # Always generate predictions, using available data or synthetic data
            
            # Prepare features for expense prediction
            X_expense = pd.DataFrame({
                'day_of_week': [(datetime.now() + timedelta(days=i)).weekday() for i in range(days)],
                'day_of_month': [(datetime.now() + timedelta(days=i)).day for i in range(days)],
                'month': [(datetime.now() + timedelta(days=i)).month for i in range(days)]
            })
            
            # If we have enough real data, use it
            if len(daily_expenses) >= 5:
                # Train expense prediction model on real data
                X_train = pd.DataFrame({
                    'day_of_week': daily_expenses['date'].apply(lambda x: pd.Timestamp(x).weekday()),
                    'day_of_month': daily_expenses['date'].apply(lambda x: pd.Timestamp(x).day),
                    'month': daily_expenses['date'].apply(lambda x: pd.Timestamp(x).month)
                })
                y_train = daily_expenses['amount']
                
                model = LinearRegression()
                model.fit(X_train, y_train)
                
                # Make predictions
                expense_predictions = model.predict(X_expense)
                expense_predictions = np.maximum(expense_predictions, 0)  # Ensure no negative expenses
                
                # Use real average for baseline
                avg_expense = daily_expenses['amount'].mean()
                
                # Note about data quality
                if len(daily_expenses) < 10:
                    st.info("Limited historical data available. Predictions may improve with more transaction history.")
            else:
                # Use synthetic data for demonstration
                st.info("Limited transaction data. Showing demo prediction.")
                
                # Generate synthetic daily expenses
                synthetic_dates = pd.date_range(start=datetime.now() - timedelta(days=60), end=datetime.now(), freq='D')
                synthetic_amounts = np.random.normal(100, 30, size=len(synthetic_dates))
                
                # Create synthetic features
                X_synthetic = pd.DataFrame({
                    'day_of_week': synthetic_dates.dayofweek,
                    'day_of_month': synthetic_dates.day,
                    'month': synthetic_dates.month
                })
                
                # Train model on synthetic data
                model = LinearRegression()
                model.fit(X_synthetic, synthetic_amounts)
                
                # Make predictions
                expense_predictions = model.predict(X_expense)
                expense_predictions = np.maximum(expense_predictions, 0)
                
                # Use synthetic average for baseline
                avg_expense = np.mean(synthetic_amounts)
            
            # Create forecast DataFrame
            forecast_dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
            df_forecast = pd.DataFrame({
                'Date': forecast_dates,
                'Predicted Expense': expense_predictions
            })
            
            # Display forecast chart
            st.subheader(f"{days}-Day Expense Forecast")
            fig = px.line(
                df_forecast,
                x='Date',
                y='Predicted Expense',
                markers=True
            )
            
            # Add baseline
            fig.add_scatter(
                x=df_forecast['Date'],
                y=[avg_expense] * len(df_forecast),
                name='Average Expense',
                line=dict(dash='dash')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate risk level
            total_predicted = sum(expense_predictions)
            baseline_total = avg_expense * days
            percent_increase = (total_predicted - baseline_total) / baseline_total * 100
            
            # Determine risk level
            if percent_increase <= 10:
                risk_level = "Safe"
                risk_class = "risk-safe"
            elif percent_increase <= 25:
                risk_level = "Medium"
                risk_class = "risk-medium"
            else:
                risk_level = "High"
                risk_class = "risk-high"
            
            # Display risk level
            st.subheader("Risk Assessment")
            st.markdown(f"""
                <div class="risk-card {risk_class}">
                    <h2>{risk_level}</h2>
                    <p>Predicted spending is {percent_increase:.1f}% {
                    'above' if percent_increase > 0 else 'below'} baseline</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Key insights
            st.subheader("Key Insights")
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                📊 Forecast Summary:
                - Average daily spend: ${np.mean(expense_predictions):.2f}
                - Peak spend day: ${max(expense_predictions):.2f}
                - Total forecast: ${sum(expense_predictions):.2f}
                """)
            
            with col2:
                st.info(f"""
                💡 Recommendations:
                - {'Consider reducing discretionary spending' if percent_increase > 20 else 'Spending pattern looks healthy'}
                - {'Set up spending alerts' if risk_level == 'High' else 'Continue monitoring trends'}
                """)
                
            # Show warning if using synthetic data
            if len(daily_expenses) < 5:
                st.warning("This is a demo prediction. Add more transactions for accurate predictions.")
        else:
            st.warning("No expense data found. Please add some transactions first.")
        
        #st.markdown('</div>', unsafe_allow_html=True)

    # Anomaly Detection Model
    elif selected_model == "Anomaly Detection":
        st.header("Anomaly Detection")
        # st.markdown('<div class="model-card">', unsafe_allow_html=True)
        
        if len(expense_df) >= 5:  # Reduced threshold for anomaly detection
            # Prepare features for anomaly detection
            features = ['amount', 'day_of_week', 'day_of_month']
            X = expense_df[features].copy()
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train isolation forest model with adjusted contamination based on data size
            contamination = 0.1 if len(expense_df) < 20 else 0.05
            model = IsolationForest(contamination=contamination, random_state=42)
            expense_df['anomaly'] = model.fit_predict(X_scaled)
            expense_df['anomaly_score'] = model.score_samples(X_scaled)
            
            # Identify anomalies
            anomalies = expense_df[expense_df['anomaly'] == -1].copy()
            
            # Display anomalies
            st.subheader("Unusual Spending Detected")
            
            if not anomalies.empty:
                # Sort anomalies by score (most anomalous first)
                anomalies = anomalies.sort_values('anomaly_score')
                
                # Display anomaly chart
                fig = px.scatter(
                    expense_df,
                    x='date',
                    y='amount',
                    color=expense_df['anomaly'].map({1: 'Normal', -1: 'Anomaly'}),
                    color_discrete_map={'Normal': 'blue', 'Anomaly': 'red'},
                    hover_data=['description', 'category'],
                    title="Transaction Anomalies"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display anomaly table
                st.subheader("Anomalous Transactions")
                anomaly_table = anomalies[['date', 'description', 'amount', 'category']].reset_index(drop=True)
                anomaly_table['date'] = anomaly_table['date'].dt.strftime('%Y-%m-%d')
                st.dataframe(anomaly_table, use_container_width=True)
                
                # Anomaly insights
                st.subheader("Anomaly Insights")
                
                # Calculate statistics
                avg_normal = expense_df[expense_df['anomaly'] == 1]['amount'].mean()
                avg_anomaly = anomalies['amount'].mean()
                percent_diff = (avg_anomaly - avg_normal) / avg_normal * 100
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"""
                    📊 Anomaly Statistics:
                    - Number of anomalies: {len(anomalies)}
                    - Average anomaly amount: ${avg_anomaly:.2f}
                    - {abs(percent_diff):.1f}% {'higher' if percent_diff > 0 else 'lower'} than normal transactions
                    """)
                
                with col2:
                    st.info(f"""
                    💡 Recommendations:
                    - Review these unusual transactions
                    - Check for potential fraud or billing errors
                    - Consider setting spending limits for these categories
                    """)
                
                # Note about data quality
                if len(expense_df) < 20:
                    st.info("Limited transaction data available. Anomaly detection will improve with more data.")
            else:
                st.success("No anomalies detected in your spending patterns!")
        else:
            # Generate synthetic data for demonstration
            st.info("Not enough real transaction data. Showing demo anomaly detection.")
            
            # Generate synthetic data
            np.random.seed(42)
            n_samples = 100
            dates = pd.date_range(start=datetime.now() - timedelta(days=60), end=datetime.now(), freq='D')
            dates = np.random.choice(dates, n_samples)
            
            # Generate mostly normal amounts with a few outliers
            amounts = np.random.normal(100, 20, n_samples)
            # Add some outliers
            outlier_indices = np.random.choice(range(n_samples), 5, replace=False)
            amounts[outlier_indices] = np.random.normal(300, 50, 5)
            
            # Create synthetic DataFrame
            synthetic_df = pd.DataFrame({
                'date': dates,
                'amount': amounts,
                'description': ['Demo transaction'] * n_samples,
                'category': np.random.choice(['Groceries', 'Dining', 'Shopping', 'Utilities'], n_samples),
                'day_of_week': pd.DatetimeIndex(dates).dayofweek,
                'day_of_month': pd.DatetimeIndex(dates).day
            })
            
            # Scale features
            X = synthetic_df[['amount', 'day_of_week', 'day_of_month']]
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train isolation forest model
            model = IsolationForest(contamination=0.05, random_state=42)
            synthetic_df['anomaly'] = model.fit_predict(X_scaled)
            
            # Identify anomalies
            anomalies = synthetic_df[synthetic_df['anomaly'] == -1].copy()
            
            # Display anomaly chart
            fig = px.scatter(
                synthetic_df,
                x='date',
                y='amount',
                color=synthetic_df['anomaly'].map({1: 'Normal', -1: 'Anomaly'}),
                color_discrete_map={'Normal': 'blue', 'Anomaly': 'red'},
                hover_data=['category'],
                title="Demo: Transaction Anomalies"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Display demo insights
            st.subheader("Demo Anomaly Insights")
            st.info("""
            This is a demonstration of anomaly detection using synthetic data.
            Add more real transactions to see anomaly detection on your actual spending patterns.
            """)
        
        # st.markdown('</div>', unsafe_allow_html=True)

    # Spending Behavior Clustering
    elif selected_model == "Spending Behavior Clustering":
        st.header("Spending Behavior Clustering")
        # st.markdown('<div class="model-card">', unsafe_allow_html=True)
        
        # Get unique categories
        categories = expense_df['category'].unique().tolist()
        
        if len(categories) >= 2:  # Need at least 2 categories for basic clustering
            # Aggregate expenses by category
            category_expenses = expense_df.groupby('category')['amount'].agg(['sum', 'mean', 'count']).reset_index()
            
            # Prepare features for clustering
            X = category_expenses[['sum', 'mean', 'count']].copy()
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Determine optimal number of clusters based on data size
            n_clusters = min(3, len(category_expenses))
            
            # Apply KMeans clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            category_expenses['cluster'] = kmeans.fit_predict(X_scaled)
            
            # Map clusters to meaningful labels
            cluster_means = category_expenses.groupby('cluster')['sum'].mean().sort_values()
            cluster_labels = {
                cluster_means.index[0]: "Low Spending",
                cluster_means.index[-1]: "High Spending"
            }
            
            if n_clusters > 2:
                cluster_labels[cluster_means.index[1]] = "Medium Spending"
            
            category_expenses['spending_level'] = category_expenses['cluster'].map(cluster_labels)
            
            # Display clustering results
            st.subheader("Spending Categories Grouped by Behavior")
            
            # Create visualization
            fig = px.bar(
                category_expenses,
                x='category',
                y='sum',
                color='spending_level',
                color_discrete_map={
                    "Low Spending": "green",
                    "Medium Spending": "orange",
                    "High Spending": "red"
                },
                title="Category Spending Clusters"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Display cluster details
            st.subheader("Spending Behavior Analysis")
            
            # High spending categories
            high_spending = category_expenses[category_expenses['spending_level'] == "High Spending"]
            if not high_spending.empty:
                st.warning("**High Spending Categories:**")
                for _, row in high_spending.iterrows():
                    st.write(f"- {row['category']}: ${row['sum']:.2f} total, ${row['mean']:.2f} average per transaction")
            
            # Medium spending categories
            if n_clusters > 2:
                medium_spending = category_expenses[category_expenses['spending_level'] == "Medium Spending"]
                if not medium_spending.empty:
                    st.info("**Medium Spending Categories:**")
                    for _, row in medium_spending.iterrows():
                        st.write(f"- {row['category']}: ${row['sum']:.2f} total, ${row['mean']:.2f} average per transaction")
            
            # Low spending categories
            low_spending = category_expenses[category_expenses['spending_level'] == "Low Spending"]
            if not low_spending.empty:
                st.success("**Low Spending Categories:**")
                for _, row in low_spending.iterrows():
                    st.write(f"- {row['category']}: ${row['sum']:.2f} total, ${row['mean']:.2f} average per transaction")
            
            # Recommendations based on clusters
            st.subheader("Recommendations")
            if not high_spending.empty:
                st.info(f"""
                💡 Budget Optimization:
                - Focus on reducing spending in {', '.join(high_spending['category'].tolist())}
                - Consider setting budget limits for high-spending categories
                - Look for alternatives or discounts in these areas
                """)
                
            # Note about data quality
            if len(expense_df) < 20:
                st.info("Limited transaction data available. Clustering will improve with more data.")
        else:
            # Generate synthetic data for demonstration
            st.info("Not enough categories for clustering. Showing demo clustering.")
            
            # Create synthetic category data
            categories = ['Groceries', 'Dining Out', 'Entertainment', 'Transportation', 'Shopping', 'Utilities', 'Rent']
            sums = [450, 200, 150, 120, 300, 180, 1200]
            means = [90, 40, 50, 30, 75, 180, 1200]
            counts = [5, 5, 3, 4, 4, 1, 1]
            
            # Create synthetic DataFrame
            synthetic_df = pd.DataFrame({
                'category': categories,
                'sum': sums,
                'mean': means,
                'count': counts
            })
            
            # Scale features
            X = synthetic_df[['sum', 'mean', 'count']]
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Apply KMeans clustering
            kmeans = KMeans(n_clusters=3, random_state=42)
            synthetic_df['cluster'] = kmeans.fit_predict(X_scaled)
            
            # Map clusters to meaningful labels
            cluster_means = synthetic_df.groupby('cluster')['sum'].mean().sort_values()
            cluster_labels = {
                cluster_means.index[0]: "Low Spending",
                cluster_means.index[1]: "Medium Spending",
                cluster_means.index[2]: "High Spending"
            }
            
            synthetic_df['spending_level'] = synthetic_df['cluster'].map(cluster_labels)
            
            # Display demo clustering results
            st.subheader("Demo: Spending Categories Grouped by Behavior")
            
            # Create visualization
            fig = px.bar(
                synthetic_df,
                x='category',
                y='sum',
                color='spending_level',
                color_discrete_map={
                    "Low Spending": "green",
                    "Medium Spending": "orange",
                    "High Spending": "red"
                },
                title="Demo: Category Spending Clusters"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Display demo insights
            st.warning("This is a demonstration using synthetic data. Add more transactions with different categories to see clustering on your actual spending patterns.")
        
        # st.markdown('</div>', unsafe_allow_html=True)

    # Future Expense Prediction
    elif selected_model == "Future Expense Prediction":
        st.header("Future Expense Prediction")
        # st.markdown('<div class="model-card">', unsafe_allow_html=True)
        
        # Get categories for prediction
        categories = expense_df['category'].unique().tolist()
        
        if len(categories) > 0:
            # Select category for prediction
            selected_category = st.selectbox("Select Category to Predict", categories)
            
            # Filter data for selected category
            category_data = expense_df[expense_df['category'] == selected_category].copy()
            
            # Ensure we have at least some data points
            if len(category_data) >= 3:
                # Aggregate by date
                daily_category = category_data.groupby(category_data['date'].dt.date)['amount'].sum().reset_index()
                daily_category['date'] = pd.to_datetime(daily_category['date'])
                
                # Create time features
                daily_category['day_of_week'] = daily_category['date'].dt.dayofweek
                daily_category['day_of_month'] = daily_category['date'].dt.day
                daily_category['month'] = daily_category['date'].dt.month
                
                # Prepare features
                X = daily_category[['day_of_week', 'day_of_month', 'month']]
                y = daily_category['amount']
                
                # Train model
                model = LinearRegression()
                model.fit(X, y)
                
                # Forecast for next 30 days
                future_dates = [datetime.now() + timedelta(days=i) for i in range(1, 31)]
                future_X = pd.DataFrame({
                    'day_of_week': [d.weekday() for d in future_dates],
                    'day_of_month': [d.day for d in future_dates],
                    'month': [d.month for d in future_dates]
                })
                
                # Make predictions
                predictions = model.predict(future_X)
                predictions = np.maximum(predictions, 0)  # Ensure no negative predictions
                
                # Create forecast DataFrame
                forecast_df = pd.DataFrame({
                    'date': future_dates,
                    'predicted_amount': predictions
                })
                
                # Display forecast chart
                st.subheader(f"30-Day Forecast for {selected_category}")
                fig = px.line(
                    forecast_df,
                    x='date',
                    y='predicted_amount',
                    markers=True,
                    title=f"Predicted {selected_category} Expenses"
                )
                
                # Add historical data points
                fig.add_scatter(
                    x=daily_category['date'],
                    y=daily_category['amount'],
                    mode='markers',
                    name='Historical Data',
                    marker=dict(color='red')
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate statistics
                total_predicted = sum(predictions)
                avg_predicted = np.mean(predictions)
                max_predicted = np.max(predictions)
                max_date = future_dates[np.argmax(predictions)].strftime('%Y-%m-%d')
                
                # Display insights
                st.subheader("Prediction Insights")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"""
                    📊 Forecast Summary:
                    - Total predicted spending: ${total_predicted:.2f}
                    - Average daily spending: ${avg_predicted:.2f}
                    - Highest predicted expense: ${max_predicted:.2f} on {max_date}
                    """)
                
                with col2:
                    # Compare with historical average
                    hist_avg = daily_category['amount'].mean()
                    percent_change = (avg_predicted - hist_avg) / hist_avg * 100 if hist_avg > 0 else 0
                    
                    st.info(f"""
                    💡 Analysis:
                    - {'Spending is projected to increase' if percent_change > 0 else 'Spending is projected to decrease'}
                    - {abs(percent_change):.1f}% {'higher' if percent_change > 0 else 'lower'} than historical average
                    - {'Consider budgeting more for this category' if percent_change > 10 else 'Current budget should be sufficient'}
                    """)
                
                # Add note about prediction accuracy
                if len(category_data) < 10:
                    st.info("Note: Limited historical data available. Predictions may improve with more transaction history.")
            else:
                # Generate synthetic data for this category to demonstrate functionality
                st.info(f"Limited data for {selected_category}. Showing demo prediction.")
                
                # Generate synthetic data for this category
                dates = pd.date_range(start=datetime.now() - timedelta(days=60), end=datetime.now(), freq='3D')
                amounts = np.random.normal(100, 20, size=len(dates))
                
                # Create synthetic DataFrame
                synthetic_df = pd.DataFrame({
                    'date': dates,
                    'amount': amounts,
                    'day_of_week': dates.dayofweek,
                    'day_of_month': dates.day,
                    'month': dates.month
                })
                
                # Train model on synthetic data
                X = synthetic_df[['day_of_week', 'day_of_month', 'month']]
                y = synthetic_df['amount']
                
                model = LinearRegression()
                model.fit(X, y)
                
                # Forecast for next 30 days
                future_dates = [datetime.now() + timedelta(days=i) for i in range(1, 31)]
                future_X = pd.DataFrame({
                    'day_of_week': [d.weekday() for d in future_dates],
                    'day_of_month': [d.day for d in future_dates],
                    'month': [d.month for d in future_dates]
                })
                
                # Make predictions
                predictions = model.predict(future_X)
                predictions = np.maximum(predictions, 0)
                
                # Create forecast DataFrame
                forecast_df = pd.DataFrame({
                    'date': future_dates,
                    'predicted_amount': predictions
                })
                
                # Display forecast chart
                st.subheader(f"30-Day Demo Forecast for {selected_category}")
                fig = px.line(
                    forecast_df,
                    x='date',
                    y='predicted_amount',
                    markers=True,
                    title=f"Demo Prediction for {selected_category}"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.warning("This is a demo prediction. Add more transactions for accurate predictions.")
        else:
            st.warning("No expense categories found. Please add some transactions first.")
        
        # st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("No transaction data available. Please add some transactions first.")

# Logout button
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))