print("Welcome to the world of awesome weather")

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
import os

# Load the data
'''df = pd.read_csv("weather_data.csv", parse_dates=["DateTime"])

# Title
st.title("City Weather Dashboard")

# City selector
cities = df["City"].unique()
selected_city = st.selectbox("Select a City", cities)

# Filter data for selected city
city_df = df[df["City"] == selected_city].sort_values("DateTime", ascending=True)

# Latest weather info
latest = city_df.iloc[-1]

st.metric("Temperature (°C)", f"{latest['Temperature (°C)']:.1f}")
st.metric("Humidity (%)", f"{latest['Humidity (%)']:.0f}")
st.metric("Weather", latest['Weather'])
st.metric("Wind Speed (m/s)", f"{latest['Wind Speed (m/s)']:.1f}")

# Line chart - Temperature trend
st.subheader("Temperature Over Time")
fig, ax = plt.subplots()
ax.plot(city_df["DateTime"], city_df["Temperature (°C)"], marker='o')
ax.set_xlabel("Date")
ax.set_ylabel("Temperature (°C)")
ax.grid(True)
st.pyplot(fig)'''

# ------------------ API Setup ------------------ #
API_KEY = "4eb98d4ed346aa423fa72bea6db5107b"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
AQI_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

cities = ["Delhi", "Mumbai", "Bengaluru", "Chennai", "Kolkata"]

# ------------------ Sidebar ------------------ #
st.sidebar.title("City Selection")
selected_city = st.sidebar.selectbox("Choose a City", cities)

# ------------------ Refresh Button ------------------ #
if st.sidebar.button("Refresh Weather"):
    st.experimental_rerun()

# ------------------ Fetch Weather Data ------------------ #
params = {
    "q": selected_city,
    "appid": "4eb98d4ed346aa423fa72bea6db5107b",
    "units": "metric"
}

# ------------------ Save Weather History ------------------ #
def save_weather_data(city, temperature, humidity, wind_speed, weather_desc):
    file_path = "weather_history.csv"
    today = datetime.today().strftime('%Y-%m-%d')

    new_row = {
        "date": today,
        "city": city,
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "description": weather_desc
    }

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if ((df["date"] == today) & (df["city"] == city)).any():
            return
        else:
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row])

    df.to_csv(file_path, index=False)

# ------------------ Main App Logic ------------------ #
try:
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    # Weather Info
    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    weather_desc = data["weather"][0]["description"].title()

    st.title(f"Weather Dashboard - {selected_city}")
    st.subheader(f"Current Weather: {weather_desc}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", f"{temperature} °C")
    col2.metric("Humidity", f"{humidity} %")
    col3.metric("Wind Speed", f"{wind_speed} m/s")

    save_weather_data(selected_city, temperature, humidity, wind_speed, weather_desc)

    # ------------------ AQI Section ------------------ #
    lat = data["coord"]["lat"]
    lon = data["coord"]["lon"]

    aqi_params = {
        "lat": lat,
        "lon": lon,
        "appid": "4eb98d4ed346aa423fa72bea6db5107b"
    }
    aqi_response = requests.get(AQI_URL, params=aqi_params)
    aqi_data = aqi_response.json()

    st.markdown("---")
    st.subheader("Air Quality Index (AQI)")
    st.json(aqi_data)  # for debugging

    try:
        aqi_index = aqi_data["list"][0]["main"]["aqi"]
        components = aqi_data["list"][0]["components"]

        aqi_scale = {
            1: "🟢 Good",
            2: "🟡 Fair",
            3: "🟠 Moderate",
            4: "🔴 Poor",
            5: "🔳 Very Poor"
        }
        aqi_label = aqi_scale.get(aqi_index, "Unknown")

        st.metric(label="AQI Level", value=f"{aqi_index} - {aqi_label}")
        st.write("**Pollutants (ug/m3):**")
        st.write(f"PM2.5: {components['pm2_5']}")
        st.write(f"PM10: {components['pm10']}")
        st.write(f"CO: {components['co']}")
        st.write(f"NO₂: {components['no2']}")
        st.write(f"O₃: {components['o3']}")

    except Exception as e:
        st.error(f"Couldn't load AQI data: {e}")

    # ------------------ Historical Trend ------------------ #
    st.markdown("---")
    st.subheader(f"Temperature Trend for {selected_city}")
    try:
        history_df = pd.read_csv("weather_history.csv")
        history_df = history_df[history_df["city"] == selected_city]
        history_df["date"] = pd.to_datetime(history_df["date"])
        history_df = history_df.sort_values("date")
        temp_df = history_df[["date", "temperature"]].set_index("date")
        st.line_chart(temp_df)
    except FileNotFoundError:
        st.warning("No historical data found yet. Visit this page daily to build your dataset.")

    # ------------------ Mock 7-Day Trend ------------------ #
    st.markdown("---")
    st.subheader("7-Day Temperature Trend (Sample Data)")
    today = datetime.today()
    dates = [(today - timedelta(days=i)).strftime("%d-%b") for i in range(6, -1, -1)]
    temps = [temperature + random.uniform(-2, 2) for _ in range(7)]
    df = pd.DataFrame({"Date": dates, "Temperature": temps})
    st.line_chart(df.set_index("Date"))

except requests.exceptions.RequestException as e:
    st.error(f"Failed to fetch weather data: {e}")

