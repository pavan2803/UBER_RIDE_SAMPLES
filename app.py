import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Smart Ride Analytics", layout="wide")

st.title("🚖 Smart Ride Analytics & Demand Forecasting Dashboard")

# Database connection
def get_connection():
    return sqlite3.connect("rides.db")

conn = get_connection()

# --- Sidebar Filters (FR6) ---
st.sidebar.header("Filters")

# Get unique values for filters
locations = pd.read_sql("SELECT DISTINCT pickup_location FROM rides", conn)['pickup_location'].tolist()
dates = pd.read_sql("SELECT DISTINCT date FROM rides ORDER BY date", conn)['date'].tolist()

selected_locations = st.sidebar.multiselect("Select Pickup Locations", locations, default=locations)
date_range = st.sidebar.date_input("Select Date Range", 
                                   [pd.to_datetime(min(dates)), pd.to_datetime(max(dates))])

# Base Query with Filters
filter_query = f"""
WHERE r.pickup_location IN ({','.join(['?']*len(selected_locations))})
AND r.date BETWEEN ? AND ?
"""
params = list(selected_locations) + [date_range[0].strftime('%Y-%m-%d'), date_range[1].strftime('%Y-%m-%d')]

# --- KPI Metrics (FR4 & FR6) ---
kpi_query = f"""
SELECT 
    COUNT(r.ride_id) as total_trips,
    SUM(t.fare_amount) as total_revenue,
    AVG(t.fare_amount) as avg_fare,
    AVG(r.ride_duration_min) as avg_duration
FROM rides r
JOIN transactions t ON r.ride_id = t.ride_id
{filter_query}
"""
kpi_data = pd.read_sql(kpi_query, conn, params=params).iloc[0]

st.subheader("📊 Key Performance Indicators")
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
col_kpi1.metric("Total Trips", f"{kpi_data['total_trips']:,}")
col_kpi2.metric("Total Revenue", f"${kpi_data['total_revenue']:,.2f}")
col_kpi3.metric("Avg Fare", f"${kpi_data['avg_fare']:,.2f}")
col_kpi4.metric("Avg Duration", f"{kpi_data['avg_duration']:.1f} min")

st.divider()

# --- Layout ---
col1, col2 = st.columns(2)

with col1:
    # 1. Peak Demand Hours (FR4)
    peak_query = f"""
    SELECT hour, COUNT(*) as total_rides
    FROM rides r
    {filter_query}
    GROUP BY hour
    ORDER BY hour
    """
    peak = pd.read_sql(peak_query, conn, params=params)
    st.subheader("📈 Total Trips per Hour")
    if not peak.empty:
        st.bar_chart(peak.set_index("hour"))
    else:
        st.write("No data for selected filters.")

with col2:
    # 2. Revenue Trends (FR4)
    revenue_trend_query = f"""
    SELECT r.date, SUM(t.fare_amount) as revenue
    FROM rides r
    JOIN transactions t ON r.ride_id = t.ride_id
    {filter_query}
    GROUP BY r.date
    ORDER BY r.date
    """
    revenue_trend = pd.read_sql(revenue_trend_query, conn, params=params)
    st.subheader("💰 Revenue Trends per Day")
    if not revenue_trend.empty:
        st.line_chart(revenue_trend.set_index("date"))
    else:
        st.write("No data for selected filters.")

# --- Row 2 ---
col3, col4 = st.columns(2)

with col3:
    # 3. Peak Pickup Locations (FR4)
    peak_zones_query = f"""
    SELECT pickup_location, COUNT(*) as trip_count
    FROM rides r
    {filter_query}
    GROUP BY pickup_location
    ORDER BY trip_count DESC
    LIMIT 5
    """
    peak_zones = pd.read_sql(peak_zones_query, conn, params=params)
    st.subheader("📍 Peak Pickup Zones")
    if not peak_zones.empty:
        st.bar_chart(peak_zones.set_index("pickup_location"))
    else:
        st.write("No data for selected filters.")

with col4:
    # 4. Average Ride Metrics (FR4)
    avg_metrics_query = f"""
    SELECT day_of_week, AVG(ride_duration_min) as avg_duration, AVG(distance_km) as avg_distance
    FROM rides r
    {filter_query}
    GROUP BY day_of_week
    """
    avg_metrics = pd.read_sql(avg_metrics_query, conn, params=params)
    st.subheader("🕒 Avg Duration & Distance by Day")
    if not avg_metrics.empty:
        st.dataframe(avg_metrics, use_container_width=True)
    else:
        st.write("No data for selected filters.")

# --- Forecasting (Still present but kept separate) ---
st.divider()
st.subheader("🔮 7-Day Demand Forecast")

# Forecasting usually works on full historical data or we can apply filters
df_forecast = pd.read_sql("SELECT date FROM rides", conn)
df_forecast['date'] = pd.to_datetime(df_forecast['date'])
daily = df_forecast.groupby('date').size().reset_index(name='rides')
daily['date_num'] = daily['date'].map(pd.Timestamp.toordinal)

X = daily[['date_num']]
y = daily['rides']

model = LinearRegression()
model.fit(X, y)

future_dates = pd.date_range(daily['date'].max(), periods=7)
future_num = pd.DataFrame({
    'date_num': future_dates.map(pd.Timestamp.toordinal)
})

predictions = model.predict(future_num)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(daily['date'], daily['rides'], label='Historical', marker='o')
ax.plot(future_dates, predictions, label='Forecast', linestyle='--', marker='x')
ax.set_title("Ride Demand Forecast")
ax.legend()
st.pyplot(fig)

conn.close()
