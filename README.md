# WalletGenie 🧞‍♂️

A smart personal finance management web application built with Streamlit and Firebase.

## 🌟 Features

- **User Authentication**: Secure login and signup with Firebase
- **Dashboard**: Overview of financial status with interactive charts
- **Transaction Management**: Easy transaction entry with AI category prediction
- **AI Predictions**: Smart spending forecasts and risk analysis
- **Budget Planning**: Interactive budget management with recommendations
- **Reports & Charts**: Comprehensive financial visualization
- **Smart Sync**: Automatic transaction synchronization
- **Goal Tracking**: Set and monitor financial goals

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wallet-genie.git
cd wallet-genie
```

2. Install dependencies:
```bash
pip install -r requirement.txt
```

3. Set up Firebase:
- Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
- Download the service account key and save as `wallet-3f13a-d7fbf39fbb1b.json`
- Create `firebase_config.json` with your web app configuration

4. Run the application:
```bash
streamlit run login.py
```

## 📂 Project Structure

```
wallet-genie/
├── login.py                 # Authentication page
├── auth_guard.py           # Authentication utilities
├── firebase_config.json    # Firebase configuration
├── pages/
│   ├── Dashboard.py        # Main dashboard
│   ├── Add Transaction.py  # Transaction entry
│   ├── AI Predictions.py   # Spending forecasts
│   ├── Budget Planner.py   # Budget management
│   ├── Reports & Charts.py # Financial reports
│   ├── Smart Sync.py       # Auto synchronization
│   └── Goal Tracker.py     # Goal management
└── requirement.txt         # Python dependencies
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
- **Database**: Firebase Realtime Database (configured)
- **Charts**: Plotly
- **Data Processing**: Pandas, NumPy

## 🔄 Smart Sync Feature

The Smart Sync feature provides:
- Automatic transaction synchronization
- Real-time balance updates
- Connection status monitoring
- Sync frequency configuration

## 📊 Reports & Analytics

Generate comprehensive financial reports with:
- Monthly spending trends
- Category-wise analysis
- Custom date range selection
- Downloadable PDF reports

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