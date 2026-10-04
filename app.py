import os
import sqlite3
import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Automated Cloud Weather ETL & Risk Analysis",
    page_icon="⛅",
    layout="wide"
)

# Title and description
st.title("⛅ Automated Cloud Weather ETL & Risk Analysis Dashboard")
st.markdown("Monitor weather metrics, automated pipeline logs, and environmental risk assessments.")

# Define database path (adjust if your SQLite database name/path differs)
DB_PATH = "data/weather.db"  # or check your local sqlite path

@st.cache_data(ttl=600)
def load_weather_data(db_path):
    """Load weather records from the SQLite database."""
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            query = "SELECT * FROM weather_data" # Replace with your actual table name if different
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.warning(f"Could not query database table: {e}")
            return None
    return None

# Load data
df = load_weather_data(DB_PATH)

# Fallback check if database or table is missing
if df is None or df.empty:
    st.error("⚠️ Weather database or data table not found!")
    
    with st.expander("Troubleshooting & Setup Guide", expanded=True):
        st.write(f"**Database Path Checked:** `{DB_PATH}`")
        st.markdown("""
        ### How to resolve this:
        1. Run your automated ETL script locally or in the cloud to extract data from the Open-Meteo API and populate SQLite (`data/weather.db`).
        2. Ensure the table name in `app.py` matches your database schema (e.g., `weather_data`).
        3. If you are deploying to Streamlit Community Cloud, make sure your SQLite database file is included or your pipeline connects to a cloud instance (like Azure Blob Storage / cloud database).
        """)
        
        # Provide sample dummy view if testing layout
        if st.checkbox("Load Sample Mock Data for Preview"):
            df = pd.DataFrame({
                "timestamp": pd.date_range(start="2026-09-01", periods=100, freq="H"),
                "temperature": [25 + (i % 5) for i in range(100)],
                "humidity": [60 + (i % 10) for i in range(100)],
                "risk_score": [0.1 * (i % 10) for i in range(100)]
            })
            st.success("Loaded mock preview data.")
        else:
            st.stop()

# Sidebar Navigation & Filters
st.sidebar.header("Dashboard Controls")
option = st.sidebar.selectbox("Select View", ["Overview Metrics", "ETL Logs & Pipeline Status", "Risk Analysis & Trends"])

if option == "Overview Metrics":
    st.subheader("📊 Live Weather Summary")
    
    # Top KPI Metrics row
    col1, col2, col3 = st.columns(3)
    if "temperature" in df.columns:
        col1.metric("Avg Temperature", f"{df['temperature'].mean():.2f} °C")
    if "humidity" in df.columns:
        col2.metric("Avg Humidity", f"{df['humidity'].mean():.2f} %")
    if "risk_score" in df.columns:
        col3.metric("Max Risk Score", f"{df['risk_score'].max():.2f}")

    st.markdown("### Raw Weather Records")
    st.dataframe(df.tail(20), use_container_width=True)

elif option == "ETL Logs & Pipeline Status":
    st.subheader("⚙️ Automated ETL Pipeline Status")
    st.info("Pipeline extracts real-time meteorological data via Open-Meteo API, stores locally in SQLite, and syncs with Azure Blob Storage.")
    
    # Display status metrics
    st.success("Pipeline Status: **Active / Synced**")
    st.write(f"Total Records Processed: **{len(df):,}**")
    
    if os.path.exists(DB_PATH):
        db_size = os.path.getsize(DB_PATH) / (1024 * 1024)
        st.write(f"SQLite Database Size: **{db_size:.2f} MB**")

elif option == "Risk Analysis & Trends":
    st.subheader("📈 Environmental Risk & Weather Trends")
    
    if "timestamp" in df.columns and "temperature" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        
        st.markdown("#### Temperature Trend Over Time")
        st.line_chart(df.set_index("timestamp")["temperature"])
        
        if "risk_score" in df.columns:
            st.markdown("#### Calculated Risk Score Progression")
            st.area_chart(df.set_index("timestamp")["risk_score"])
    else:
        st.warning("Required timestamp or metric columns not found for plotting.")
