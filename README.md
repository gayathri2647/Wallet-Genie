# WalletGenie 🧞‍♂️

A smart personal finance management web application built with Streamlit and Firebase.

## 🌟 Features

- **User Authentication**: Secure login and signup with Firebase
- **Dashboard**: Overview of financial status with interactive charts
- **Transaction Management**: Easy transaction entry with AI category prediction
- **AI Predictions**: Smart spending forecasts and risk analysis
- **Budget Planning**: Interactive budget management with recommendations
- **Transaction History**: Comprehensive view of past transactions
- **Goal Tracking**: Set and monitor financial goals
- **Settings**: Personalize your WalletGenie experience

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wallet-genie.git
cd wallet-genie
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Firebase:
- Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
- Download the service account key and save as `firebase_key.json`
- For local development:
  - Copy `.env.example` to `.env` and fill in your Firebase configuration, OR
  - Create `.streamlit/secrets.toml` with your Firebase credentials (see `secrets.toml.example`)
- Run `python -c "from config_loader import create_firebase_config_file; create_firebase_config_file()"` to generate the config file

4. For Streamlit Cloud deployment:
- Go to your app settings in the Streamlit Cloud dashboard
- Navigate to the "Secrets" section
- Add your Firebase credentials in the same format as in `secrets.toml.example`

4. Run the application:
```bash
streamlit run login.py
```

## 📂 Project Structure

```
wallet-genie/
├── login.py                 # Authentication page
├── auth_guard.py            # Authentication utilities
├── firebase_config.json     # Firebase configuration
├── firebase_key.json        # Firebase service account key
├── config.py                # Application configuration
├── shared_utils.py          # Shared utility functions
├── pages/
    ├── 1_Add Transaction.py # Transaction entry
    ├── 2_Dashboard.py       # Main dashboard
    ├── 3_Transaction History.py # Transaction history
    ├── AI Predictions.py    # Spending forecasts and analysis
    ├── Budget Planner.py    # Budget management
    └── Goal Tracker.py      # Goal management
    └── Settings.py          # Application settings

```

## 🔒 Authentication

The app uses Firebase Authentication for secure user management. Features include:
- Email/Password authentication
- Password reset
- Session management
- Protected routes

## 🎨 UI/UX

- **Theme**: Royal blue + mint green color scheme
- **Layout**: Responsive design with card layouts
- **Components**: Interactive charts, progress bars, and metrics
- **Navigation**: Consistent sidebar with logout button

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Authentication**: Firebase Auth
- **Database**: Firebase Firestore
- **Charts**: Plotly
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: scikit-learn for predictions and clustering

## 📊 AI Prediction Features

WalletGenie includes several AI-powered features:
- **Income/Expense Prediction**: Forecast future financial patterns
- **Anomaly Detection**: Identify unusual spending patterns
- **Spending Behavior Clustering**: Group expenses by spending behavior
- **Future Expense Prediction**: Category-specific spending forecasts

## 🎯 Goal Tracking

Track financial goals with:
- Progress visualization
- Deadline monitoring
- Smart alerts for off-track goals
- Goal analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Streamlit for the amazing framework
- Firebase for authentication and database services
- The open-source community for inspiration and resources

## 👥 Project Contributors

This project was developed by:


- [**Yugesh A**](https://github.com/Yugesh-003) — Developer, Backend Integration
- [**Gayathri Prasad M N**](https://github.com/gayathri2647) — Developer, UI Design  

We worked together to build, design, and implement the features of this project.
