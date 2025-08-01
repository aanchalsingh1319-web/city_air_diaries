print("Welcome to the world of awesome weather")

# Triggering redeploy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
import os

# Load the data
df = pd.read_csv("weather_data.csv", parse_dates=["DateTime"])

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
st.pyplot(fig)

# ------------------ API Setup ------------------ #
API_KEY = "4eb98d4ed346aa423fa72bea6db5107b"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
AQI_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

cities = ["Delhi", "Mumbai", "Bengaluru", "Chennai", "Kolkata"]

# ------------------ Sidebar ------------------ #
st.sidebar.title("City Selection")
selected_cities = st.sidebar.multiselect("Choose Cities to Compare", cities, default=["Delhi"])
show_comparison = st.sidebar.checkbox("Show city comparison?", value=False)
# ------------------ Refresh Button ------------------ #
if st.sidebar.button("Refresh Weather"):
    st.experimental_rerun()

if show_comparison:
    st.markdown("---")
    st.subheader("City Comparison")

    st.write("Running city comparison block...")

    comparison_data = []

    for city in selected_cities:
        st.write(f"Fetching data for {city}")
        try:
            params= {
                "q" : city,
                "appid": "4eb98d4ed346aa423fa72bea6db5107b",
                "units": "metric"
            }
            response = requests.get(BASE_URL, params=params)
            weather_data = response.json()
            temp = weather_data["main"]["temp"]
            humidity = weather_data["main"]["humidity"]
            wind = weather_data["wind"]["speed"]

            lat = weather_data["coord"]["lat"]
            lon = weather_data["coord"]["lon"]
            aqi_resp = requests.get(AQI_URL, params={"lat": lat, "lon": lon, "appid": API_KEY})
            aqi_index = aqi_resp.json()["list"][0]["main"]["aqi"]

            comparison_data.append({
                "City": city,
                "Temperature (°C)": temp,
                "Humidity (%)": humidity,
                "Wind Speed (m/s)": wind,
                "AQI Index": aqi_index
                })
        except Exception as e:
            st.warning(f"Failed to load data for {city}: {e}")

    if comparison_data:
        df_comp = pd.DataFrame(comparison_data).set_index("City")
        st.dataframe(df_comp)

        st.markdown("###City Metrics")
        st.bar_chart(df_comp[["Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)"]])

        st.markdown("###AQI Comparison")
        st.bar_chart(df_comp[["AQI Index"]])
    else:
        st.warning("No comparison data available.")

# ------------------ Fetch Weather Data ------------------ #
params = {
    "q": selected_city,
    "appid": "4eb98d4ed346aa423fa72bea6db5107b",
    "units": "metric"
}

# ------------------ Save Weather History ------------------ #
def save_weather_data_to_gsheet(city, temperature, humidity, wind_speed, weather_desc):
    from gspread_dataframe import set_with_dataframe

    today = datetime.today().strftime('%Y-%m-%d')
    new_row = pd.DataFrame([{
        "date": today,
        "city": city,
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "description": weather_desc
    }])

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    # 🧪 DEBUG 1: Confirm sheet open
    try:
        sheet = client.open("City Air Diaries Weather Log")
        st.write("Opened Google Sheet successfully")
    except Exception as e:
        st.error(f"Failed to open sheet: {e}")
        return

    try:
        worksheet = sheet.worksheet(city)
        st.write(f"Worksheet for {city} found")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=city, rows="100", cols="10")
        st.write(f"Created new worksheet for {city}")

    # Get existing data
    existing_data = worksheet.get_all_records()
    df_existing = pd.DataFrame(existing_data)

    # Avoid duplicates
    if not df_existing.empty and ((df_existing["date"] == today) & (df_existing["city"] == city)).any():
        st.warning(f"Data for {city} on {today} already exists.")
        return

    # Write updated data
    df_combined = pd.concat([df_existing, new_row], ignore_index=True) if not df_existing.empty else new_row
    worksheet.clear()
    set_with_dataframe(worksheet, df_combined)
    st.success(f"Data saved to Google Sheet for {city} on {today}")




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

    save_weather_data_to_gsheet(selected_city, temperature, humidity, wind_speed, weather_desc)

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
        if history_df.empty:
            st.warning(f"No historical data for {selected_city} yet.")
        else:
            temp_df = history_df[["date", "temperature"]].set_index("date")
            st.line_chart(temp_df)
        history_df = history_df.sort_values("date")
        temp_df = history_df[["date", "temperature"]].set_index("date")
        st.line_chart(temp_df)
    except FileNotFoundError:
        st.warning("No historical data found yet. Visit this page daily to build your dataset.")



    # ------------------ Download Weather History CSV ------------------ #

    st.markdown("---")
    st.subheader("📥 Export Weather History")

    if os.path.exists("weather_history.csv"):
        df_all = pd.read_csv("weather_history.csv")
        df_city = df_all[df_all["city"] == selected_city]

        if not df_city.empty:
            csv = df_city.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"Download {selected_city} Weather History CSV",
                data=csv,
                file_name=f"{selected_city}_weather_history.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"No weather history found for {selected_city}.")
    else:
        st.warning("No weather history available for download yet.")

    # ------------------ 5-Day Forecast ------------------ #
    st.markdown("---")
    st.subheader("5-Day Forecast (Daily Avg Temperature)")

    forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
    forecast_params = {
        "q": selected_city,
        "appid": "4eb98d4ed346aa423fa72bea6db5107b",
        "units": "metric"
    }
    forecast_response = requests.get(forecast_url, params=forecast_params)
    forecast_data = forecast_response.json()

    # Process forecast data
    forecast_list = forecast_data.get("list", [])
    forecast_by_day = {}

    for entry in forecast_list:
        dt_txt = entry["dt_txt"]  # e.g., '2025-08-01 12:00:00'
        date = dt_txt.split(" ")[0]
        temp = entry["main"]["temp"]

        if date not in forecast_by_day:
            forecast_by_day[date] = []
        forecast_by_day[date].append(temp)

    # Calculate daily average temperatures
    dates = []
    avg_temps = []
    for date, temps in forecast_by_day.items():
        if len(dates) >= 5:
            break
        dates.append(date)
        avg_temps.append(sum(temps) / len(temps))

    # Plot forecast
    if dates:
        forecast_df = pd.DataFrame({
            "Date": pd.to_datetime(dates).strftime("%d %b"),
            "Avg Temp (°C)": avg_temps
        })
        st.line_chart(forecast_df.set_index("Date"))
    else:
        st.warning("Forecast data not available.")
except requests.exceptions.RequestException as e:
    st.error(f"Failed to fetch weather data: {e}")

