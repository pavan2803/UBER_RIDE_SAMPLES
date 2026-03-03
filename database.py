import pandas as pd
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("rides.db")
cursor = conn.cursor()

# Enable Foreign Key support
cursor.execute("PRAGMA foreign_keys = ON;")

# 1. Create Tables with Schema (FR5)
cursor.execute("DROP TABLE IF EXISTS transactions;")
cursor.execute("DROP TABLE IF EXISTS rides;")
cursor.execute("DROP TABLE IF EXISTS customers;")

cursor.execute("""
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE rides (
    ride_id TEXT PRIMARY KEY,
    driver_id TEXT NOT NULL,
    pickup_time DATETIME NOT NULL,
    drop_time DATETIME NOT NULL,
    pickup_location TEXT NOT NULL,
    drop_location TEXT NOT NULL,
    distance_km REAL NOT NULL,
    rating REAL,
    hour INTEGER,
    date DATE,
    day_of_week TEXT,
    ride_duration_min REAL,
    customer_id TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
)
""")

cursor.execute("""
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    ride_id TEXT NOT NULL,
    fare_amount REAL NOT NULL,
    payment_method TEXT,
    payment_status TEXT,
    FOREIGN KEY (ride_id) REFERENCES rides (ride_id)
)
""")

# 2. Load and Store Data
# Load Dataframes
rides_df = pd.read_csv("cleaned_rides.csv")
customers_df = pd.read_csv("cleaned_customers.csv")
transactions_df = pd.read_csv("cleaned_transactions.csv")

# Note: The order of insertion matters for foreign key constraints
customers_df.to_sql("customers", conn, if_exists="append", index=False)
rides_df.to_sql("rides", conn, if_exists="append", index=False)
transactions_df.to_sql("transactions", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("✅ Database Updated Successfully with Relational Integrity and Structured Tables")