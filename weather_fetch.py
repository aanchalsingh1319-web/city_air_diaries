#### Make a Weather API Call for a City

import requests
import pandas as pd
from datetime import datetime
import os

# Replace this with your actual API key inside quotes
api_key = "3d687980078ae6eb796b2051b2aba63d"

# List of cities you want to track
cities = ["Delhi", "Mumbai", "Bangalore", "Kolkata", "Chennai", "Ahmedabad"]
FILENAME = "weather_data.csv"

# Create a list to hold the data
weather_data = []


def fetch_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={"3d687980078ae6eb796b2051b2aba63d"}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        return {
            "City": city,
            "DateTime": datetime.now(),
            "Temperature (°C)": data["main"]["temp"],
            "Humidity (%)": data["main"]["humidity"],
            "Pressure (hPa)": data["main"]["pressure"],
            "Wind Speed (m/s)": data["wind"]["speed"],
            "Weather": data["weather"][0]["description"]
        }
    else:
        print(f"Failed for {city}: {data}")
        return None


# Collect data for all cities
weather_data = []
for city in cities:
    result = fetch_weather(city)
    if result:
        weather_data.append(result)

# Convert to DataFrame
df = pd.DataFrame(weather_data)

# Append to CSV (create if not exists)
if os.path.exists(FILENAME):
    df.to_csv(FILENAME, mode='a', index=False, header=False)
else:
    df.to_csv(FILENAME, index=False)

    print("Data fetched and saved!")