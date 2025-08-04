import requests
import pandas as pd
from datetime import datetime
import os

# ✅ Your OpenWeather API key
API_KEY = "4eb98d4ed346aa423fa72bea6db5107b"

# ✅ Cities to monitor
CITIES = ["Delhi", "Mumbai", "Bangalore", "Kolkata", "Chennai", "Ahmedabad", "Gurugram"]
FILENAME = "weather_history.csv"
MISSING_DATES = ["2025-07-31", "2025-08-01", "2025-08-02", "2025-08-03"]

# ✅ Function to fetch weather for a city
def fetch_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={"4eb98d4ed346aa423fa72bea6db5107b"}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        print(f"✅ Data fetched successfully for {city}")
        return {
            "date": datetime.today().strftime('%Y-%m-%d'),
            "city": city.strip().lower(),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"]
        }
    else:
        print(f"❌ Failed for {city}: {data.get('message', 'Unknown error')}")
        return None

# ✅ Load existing data from CSV (if any)
def load_existing_data():
    if os.path.exists(FILENAME):
        return pd.read_csv(FILENAME)
    else:
        return pd.DataFrame(columns=["date", "city", "temperature", "humidity", "wind_speed", "description"])

# -------- SKIP IF LOGGED --------
def already_logged(df, city, date_str):
    return not df[
        (df["city"].str.lower() == city.lower()) &
        (df["date"] == date_str)
    ].empty


# -------- MAIN BACKFILL --------
def backfill():
    existing_df = load_existing_data()
    new_entries = []

    for date_str in MISSING_DATES:
        for city in CITIES:
            if already_logged(existing_df, city, date_str):
                print(f"✅ {city} already logged for {date_str}. Skipping.")
                continue

            result = fetch_weather(city)
            if result:
                result["date"] = date_str
                new_entries.append(result)
                print(f"✔ Added {city} for {date_str}")

    if new_entries:
        df_new = pd.DataFrame(new_entries)
        df_combined = pd.concat([existing_df, df_new], ignore_index=True)
        df_combined.to_csv(FILENAME, index=False)
        print("\n✅ Backfill complete!")
    else:
        print("\n⚠️ No new data fetched. Backfill not needed.")

if __name__ == "__main__":
    backfill()

# ✅ Main routine
def main():
    today = datetime.today().strftime('%Y-%m-%d')
    existing_df = load_existing_data()
    new_data = []

    for city in CITIES:
        # Skip if today's data already exists
        if not existing_df[
            (existing_df["city"].str.lower() == city.lower()) &
            (existing_df["date"] == today)
        ].empty:
            print(f"⏩ {city} already logged today. Skipping.")
            continue

        result = fetch_weather(city)
        if result:
            new_data.append(result)

    if new_data:
        df_new = pd.DataFrame(new_data)
        df_combined = pd.concat([existing_df, df_new], ignore_index=True)
        df_combined.to_csv(FILENAME, index=False)
        print("✅ Weather history updated.")
    else:
        print("⚠ No new data added today.")

# ✅ Run main
if __name__ == "__main__":
    main()