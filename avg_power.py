# streamlit_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date

st.set_page_config(layout="wide", page_title="Power Average Calculator")

st.title("⚡ Power Average Calculator")

# --- Input Section ---
check_day = st.date_input("Select check day", value=date.today())

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file and check_day:
    try:
        # Read file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, sep=';', skiprows=1)
        else:
            df = pd.read_excel(uploaded_file, skiprows=1)

        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        # Define time ranges
        check_day_obj = datetime.combine(check_day, datetime.min.time())
        prev_day = check_day_obj - timedelta(days=1)
        next_day = check_day_obj + timedelta(days=1)
        next2_day = check_day_obj + timedelta(days=2)

        # Masks
        mask_before = (df['Timestamp'] >= prev_day) & (df['Timestamp'] < check_day_obj)
        mask_today = (df['Timestamp'] >= check_day_obj) & (df['Timestamp'] < next_day)
        mask_after = (df['Timestamp'] >= next_day) & (df['Timestamp'] < next2_day)

        # Time resolution
        interval_minutes = (df['Timestamp'].iloc[1] - df['Timestamp'].iloc[0]).seconds / 60
        kwh_factor = interval_minutes / 60

        # Energy calculations
        power_before = df.loc[mask_before, 'Power Avg [kW]'].sum() * kwh_factor
        power_today = df.loc[mask_today, 'Power Avg [kW]'].sum() * kwh_factor
        power_after = df.loc[mask_after, 'Power Avg [kW]'].sum() * kwh_factor

        # Display results
        st.subheader("🔍 Power avg Summary")
        st.write(f"**Power average before:** {power_before:.2f} kWh")
        st.write(f"**Power average:** {power_today:.2f} kWh")
        st.write(f"**Power average after:** {power_after:.2f} kWh")

        # Plot
        st.subheader("📈 Power Plot for Selected Day")
        subset = df.loc[mask_today]

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(subset['Timestamp'], subset['Power Avg [kW]'], label='Power Avg [kW]', linestyle='-')
        avg_kw = power_today / (24 * 60 / interval_minutes)
        ax.axhline(y=avg_kw, color='red', linestyle='--', label=f'Average = {power_today:.2f} kWh/day')
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Power Avg [kW]")
        ax.set_title("Power Average over Time")
        ax.legend()
        ax.grid(True)
        fig.autofmt_xdate()

        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Error: {e}")
