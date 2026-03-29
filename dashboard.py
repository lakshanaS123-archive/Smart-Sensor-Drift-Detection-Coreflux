import streamlit as st
import sqlite3
import pandas as pd
import time

st.set_page_config(page_title="Smart Sensor Monitoring", layout="wide")

st.title("Smart Sensor Drift Detection and Calibration Prediction System")

db_path = "sensor_data.db"

def load_data():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM sensor_data ORDER BY timestamp DESC", conn)
    conn.close()
    return df

while True:
    df = load_data()

    if not df.empty:
        st.subheader("Latest Sensor Data")
        st.dataframe(df.head(10))

        st.subheader("Temperature Graph")
        temp_chart = df.groupby("timestamp")["temperature"].mean()
        st.line_chart(temp_chart)

        st.subheader("Health Score Graph")
        health_chart = df.groupby("timestamp")["health"].mean()
        st.line_chart(health_chart)

        st.subheader("Sensor Drift Warning")
        for i in df["sensor_id"].unique():
            sensor_df = df[df["sensor_id"] == i]
            avg_error = sensor_df["error"].mean()
            if abs(avg_error) > 2:
                st.error(f"Sensor {i} needs calibration! Drift detected.")
            else:
                st.success(f"Sensor {i} is healthy.")

        st.subheader("Calibration Prediction")
        for i in df["sensor_id"].unique():
            sensor_df = df[df["sensor_id"] == i]
            avg_error = sensor_df["error"].mean()

            if abs(avg_error) > 4:
                st.error(f"Sensor {i}: Calibration needed immediately!")
            elif abs(avg_error) > 2:
                st.warning(f"Sensor {i}: Calibration needed soon.")
            else:
                st.success(f"Sensor {i}: No calibration needed.")

        # NEW SECTION ADDED HERE
        st.subheader("Overall System Status")

        latest_data = df.groupby("sensor_id").first().reset_index()

        for index, row in latest_data.iterrows():
            if row["health"] < 50:
                st.error(f"Sensor {row['sensor_id']} CRITICAL - Immediate Maintenance Required")
            elif row["health"] < 70:
                st.warning(f"Sensor {row['sensor_id']} WARNING - Maintenance Soon")
            else:
                st.success(f"Sensor {row['sensor_id']} OK")

        st.subheader("Download Sensor Data")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name='sensor_data.csv',
            mime='text/csv',
        )

    else:
        st.warning("No data available yet...")

    time.sleep(5)
    st.rerun()