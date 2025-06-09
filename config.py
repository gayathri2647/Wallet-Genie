"""
Global configuration settings for the WalletGenie application.
"""

# Currency settings
CURRENCY = "₹"  # Indian Rupee symbol.
CURRENCY_CODE = "INR"

# Theme settings
THEME = {
    "primaryColor": "#FF6B6B",  # Warm red
    "backgroundColor": "#F5F5F5",  # Light gray
    "secondaryBackgroundColor": "#E8F4F9",  # Light blue
    "textColor": "#333333",  # Dark gray
    "font": "sans-serif"
}

# Custom CSS for consistent styling
CUSTOM_CSS = """
    <style>
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #FF6B6B;
    }
    .warning-box {
        background-color: #ffe4e1;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ff6b6b;
        color: black;
    }
    .budget-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #4682b4;
    }
    .recommendation {
        background-color: #E8F4F9;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #4682b4;
    }
    </style>
"""