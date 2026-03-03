import pandas as pd
import numpy as np


df = pd.read_csv("rides.csv")


df['pickup_time'] = pd.to_datetime(df['pickup_time'])
df['drop_time'] = pd.to_datetime(df['drop_time'])


df['hour'] = df['pickup_time'].dt.hour
df['date'] = df['pickup_time'].dt.date
df['day_of_week'] = df['pickup_time'].dt.day_name()
df['ride_duration_min'] = (
    df['drop_time'] - df['pickup_time']
).dt.total_seconds() / 60


df = df[df['fare_amount'] > 0]
df = df[df['distance_km'] > 0]




customer_ids = [f"CUST{i:03d}" for i in range(1, 11)]
customer_names = ["John Doe", "Jane Smith", "Alice Brown", "Bob Wilson", "Charlie Davis", 
                  "Eva White", "Frank Miller", "Grace Lee", "Henry Ford", "Ivy Green"]
customers_df = pd.DataFrame({
    "customer_id": customer_ids,
    "name": customer_names,
    "email": [f"{name.lower().replace(' ', '.')}@example.com" for name in customer_names]
})


np.random.seed(42)
df['customer_id'] = np.random.choice(customer_ids, size=len(df))


transactions_df = pd.DataFrame({
    "transaction_id": [f"TXN{i:03d}" for i in range(1, len(df) + 1)],
    "ride_id": df['ride_id'].values,
    "fare_amount": df['fare_amount'].values,
    "payment_method": np.random.choice(["Credit Card", "Cash", "Wallet"], size=len(df)),
    "payment_status": "Completed"
})


rides_df = df.drop(columns=['fare_amount'])


rides_df.to_csv("cleaned_rides.csv", index=False)
customers_df.to_csv("cleaned_customers.csv", index=False)
transactions_df.to_csv("cleaned_transactions.csv", index=False)

print("✅ Data Normalization and Cleaning Completed (3 CSVs generated)")