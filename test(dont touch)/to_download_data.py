import pandas as pd

def get_user_transactions(uid):
    tx_ref = db.collection("users").document(uid).collection("transactions").stream()
    return [tx.to_dict() for tx in tx_ref]

tx_data = get_user_transactions(user_id)
df = pd.DataFrame(tx_data)

st.download_button("Download CSV", df.to_csv(index=False), "expenses.csv", "text/csv")
