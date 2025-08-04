print("Welcome to the world of awesome weather")

from geopy.geocoders import Nominatim
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import os

# ---- Config ----
st.set_page_config(page_title="City Air Diaries", layout="wide")

API_KEY = "4eb98d4ed346aa423fa72bea6db5107b"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Ahmedabad", "Gurugram"]

# ---- Sidebar ----
st.sidebar.title("City Selection")
selected_cities = st.sidebar.multiselect("Choose Cities to Compare", cities, default=["Delhi"])
show_comparison = st.sidebar.checkbox("Show city comparison?")
selected_city = st.sidebar.selectbox("Choose a City to View Details", cities)

# 🔁 Manual Update Button
if st.sidebar.button("Update All Data Now"):
    os.system("python fetch_weather_history.py")
    st.success("Weather history updated.")

if st.sidebar.button("Refresh Weather"):
    st.rerun()

# ---- Title ----
st.title("🌤️ City Weather Dashboard")

# ---- Current Weather ----
st.subheader(f"Current Weather in {selected_city}")
try:
    params = {"q": selected_city, "appid": "4eb98d4ed346aa423fa72bea6db5107b", "units": "metric"}
    r = requests.get(BASE_URL, params=params).json()
    temp = r["main"]["temp"]
    hum = r["main"]["humidity"]
    wind = r["wind"]["speed"]
    desc = r["weather"][0]["description"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature (°C)", f"{temp:.1f}")
    c2.metric("Humidity (%)", f"{hum}%")
    c3.metric("Wind Speed (m/s)", f"{wind}")

except Exception as e:
    st.error(f"Error fetching current weather: {e}")

# ----- AQI Fetch -----
st.subheader(f"Air Quality Index in {selected_city}")

try:
    geolocator = Nominatim(user_agent="city_air_diaries")
    location = geolocator.geocode(selected_city)
    lat, lon = location.latitude, location.longitude

    aqi_url = "http://api.openweathermap.org/data/2.5/air_pollution"
    aqi_params = {"lat": lat, "lon": lon, "appid": "4eb98d4ed346aa423fa72bea6db5107b"}
    aqi_resp = requests.get(aqi_url, params=aqi_params).json()

    aqi = aqi_resp["list"][0]["main"]["aqi"]

    aqi_text = {
        1: "Good 😊",
        2: "Fair 🙂",
        3: "Moderate 😐",
        4: "Poor 😷",
        5: "Very Poor 🤢"
    }

    st.metric("AQI Level", f"{aqi} - {aqi_text.get(aqi, 'Unknown')}")

except Exception as e:
    st.error(f"Error fetching AQI: {e}")

# ---- 5-day Forecast ----
st.subheader(f"5-Day Forecast for {selected_city}")
try:
    forecast_params = {"q": selected_city, "appid": "4eb98d4ed346aa423fa72bea6db5107b", "units": "metric"}
    forecast_resp = requests.get(FORECAST_URL, params=forecast_params).json()
    forecast_list = forecast_resp["list"]

    forecast_data = []
    for entry in forecast_list:
        dt_txt = entry["dt_txt"]
        temp_f = entry["main"]["temp"]
        forecast_data.append({"DateTime": dt_txt, "Temperature (°C)": temp_f})

    forecast_df = pd.DataFrame(forecast_data)
    forecast_df["DateTime"] = pd.to_datetime(forecast_df["DateTime"])

    # ---- Forecast Chart ----
    fig_forecast = px.line(
        forecast_df,
        x="DateTime",
        y="Temperature (°C)",
        title="5-Day Temperature Forecast",
        markers=True,
        hover_data=["Temperature (°C)"]
    )
    fig_forecast.update_layout(xaxis_title="DateTime", yaxis_title="Temp (°C)")
    st.plotly_chart(fig_forecast, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching forecast: {e}")

# ---- Historical Trends ----
st.subheader(f"Temperature Trend for {selected_city}")
history_file = "weather_history.csv"

if os.path.exists(history_file):
    hist_df = pd.read_csv(history_file)

    # Clean data
    hist_df = hist_df.dropna()
    hist_df.columns = hist_df.columns.str.strip().str.lower()
    hist_df["date"] = pd.to_datetime(hist_df["date"])

    city_hist = hist_df[hist_df["city"].str.lower() == selected_city.lower()]

    # ---- Historical Temperature Trend ----
    if not city_hist.empty:
        fig_hist = px.line(
            city_hist,
            x="date",
            y="temperature",
            title="Historical Temperature Trend",
            markers=True,
            hover_data=["humidity", "wind_speed", "description"]
        )
        fig_hist.update_layout(xaxis_title="Date", yaxis_title="Temp (°C)")
        st.plotly_chart(fig_hist, use_container_width=True)

        st.download_button(
            "Download Historical Data",
            city_hist.to_csv(index=False).encode(),
            file_name=f"{selected_city}_history.csv",
            mime="text/csv"
        )
    else:
        st.info("No historical data for this city.")
else:
    st.warning("Historical CSV not found.")

# ---- Comparison Table + Chart ----
if show_comparison:
    st.subheader("City Comparison")
    comp_data = []
    for c in selected_cities:
        try:
            p = {"q": c, "appid": "4eb98d4ed346aa423fa72bea6db5107b", "units": "metric"}
            resp = requests.get(BASE_URL, params=p).json()
            comp_data.append({
                "City": c,
                "Temp (°C)": resp["main"]["temp"],
                "Humidity": resp["main"]["humidity"],
                "Wind": resp["wind"]["speed"]
            })
        except:
            pass

    if comp_data:
        df_comp = pd.DataFrame(comp_data).set_index("City")
        st.dataframe(df_comp)

        df_reset = df_comp.reset_index()
        fig_comp = px.bar(
            df_reset,
            x="City",
            y=["Temp (°C)", "Humidity", "Wind"],
            barmode="group",
            title="City Comparison (Temp, Humidity, Wind)",
            hover_name="City"
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# ----- 🟢 2️⃣ City Ranking Feature -----

if show_comparison and comp_data:
    st.subheader("City Rankings")

    temp_sorted = df_comp["Temp (°C)"].sort_values(ascending=False)

    # Initialize Geolocator ----
    geolocator = Nominatim(user_agent="city_air_diaries")

    aqi_ranking = []

    for c in selected_cities:
        try:
            loc = geolocator.geocode(c)
            resp = requests.get(
                "http://api.openweathermap.org/data/2.5/air_pollution",
                params={"lat": loc.latitude, "lon": loc.longitude, "appid": "4eb98d4ed346aa423fa72bea6db5107b"}
            ).json()
            city_aqi = resp["list"][0]["main"]["aqi"]
            aqi_ranking.append((c, city_aqi))
        except:
            pass

    aqi_sorted = sorted(aqi_ranking, key=lambda x: x[1])

    st.markdown("**🌡️ Hottest Cities:**")
    st.write(temp_sorted)

    st.markdown("**🌬️ Cleanest Air:**")
    st.write(pd.DataFrame(aqi_sorted, columns=["City", "AQI"]).set_index("City"))