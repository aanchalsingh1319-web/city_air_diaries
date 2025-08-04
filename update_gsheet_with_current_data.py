import requests
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
import streamlit as st

# 🟩 Setup Google Sheets credentials from Streamlit secrets
# Use this only if you're running inside Streamlit app.
# If you're running standalone script, replace `st.secrets` with your credentials manually

# ✅ Replace this block with your service account JSON values directly if not using Streamlit
{
  "type": "service_account",
  "project_id": "weatherdiaries",
  "***REMOVED***_id": "1a54a5ed4e1856474c4876079d3dd183f0213185",
  "***REMOVED***": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDM1F0hWhKCE2Vy\naPKUtgbwlOa3ES0p85OCqKkLpul7I9TpprFzoO50dL1a0YRIpNLXMp+Y0ztDkird\nTe3wrYBufd6EpDIHpz23A8bQI/6s3KHgO/AQRWL6+DPNKPG8KGVfFHWXjZS0hrOc\nIUYupDbLZ8JgJPt/ptyGlB/h7vCQIL70pMUkWjJVI7vnv0BQxtUgaSWT9dYAKF5Q\nTj2OZlJhA2B5D7OaZOdESXVcW89CGM32AVvRZZ1sErXLtC3iHswl3hM0S287RO8E\nr65FgphoPSpASonX4p4nLE04+L4ZU0t45h4q3Akq0q0B1Qcto7IoI4AdOaoHEA5H\n3Yg1n4U7AgMBAAECggEAEJO/VcusY8qeEzxbJZ31wdLLOVWyigqkjZaI1+CSVNz5\nhk9vXSRRKCuqh4cdZaOxTKlUMVInIbjarz53W1svYcHeGG4Rfn0SiZVMqdu/6M2S\nbEttimOTNyyPRLNjnQ7H5YIKYlGbD2E3eBNZUr0Hkj67hHx5vkMK5flm+yoTXhaj\nQFYZo441P5b3+yDmFxnHeIKMDZtSG3GFStCc1FGNh+EA8+ZYEsZaVBkaDDVn9gUu\ne5gDF54AZe7Tx/b02gTCgXqLR5p23SwacG4AZijispHqrG4fUjhNidR5OrwgR7So\n+N8GbICzVwQUuqKDT2jhoHSAaGZX7T2GrD8BdG4vwQKBgQDxG8s8ahgGUpq+GmU3\nLfh+iSVB1nN7m8k3dHgklejZvKRjNzfVbC3OqNt825VO8snfS7+NLyM8w7YA5RpB\nAYU1FhG06Uc0YKeyQjM+7WlQtW151StaGuUezrTKIATnHQu3CqARncusQ8B6gTLE\nmoc4dyAMFqrfW0Uam0L1GlCWZwKBgQDZevTagYF1F/Rawbm8TCCmy0tkT+Fac6Q7\ngAo9zO+ssx1O4PXLNNrzzp5TXzWA6qr/nflHgiiBrKWZ7jENppqHs6g6qn96Mh7+\nYADV2ikR3Eo5L57P9opxunH1baQnHT9wQRjoFctBHYrfjEEOWuvGFFZtnG8dIOlE\nSd5B2tfODQKBgQCbo4ZpBE9n3XDYYG+P1BQBkoRDYKyBUUntizh23XJHA5fWF/Hp\nygAz1BqDGbfjE6SuiNYozBHiCq/1Ge79oX6cixd5AdEeBXqa/lLYPybpm4QEzk9C\nxfO7FFHt3AduLPi/+pLjbEnqdH3OVpIwCVRaZcOBKiy5K9CK4UiysX7t5wKBgF4j\nKvmqNS9KPytJz+wBx+Bq/ydcrF9KzzwyIDzACL7oiTcriTl8l4oRVdcgzzgOXBZp\new3I+V+oK8aFpBYUl69FxPwf8S4jo+bYB4SJ+l0QzdATHNtIDIVN/yYNX5DOyDb+\n9pj/VgvJjeNWApMEKCqFgyPPIwmoxVAZ6Wr4H5HBAoGAJ5yOQ29c9+a7dyggUoHm\nk++C75cbw1LYo63xHvSUHomiKNYw+9+aMQ6aygwmrFhKgo2wT0ReLZb6zlJdcPg4\nuJrS40T48xQv2FjCByzw6NMJnouaLeCnefAqu8uqbb3u/A+WBaS0B4h432oPEe1u\njZgILGpX9p4Cf9TAc0vXQsA=\n-----END PRIVATE KEY-----\n",
  "client_email": "daily-weather-logger@weatherdiaries.iam.gserviceaccount.com",
  "client_id": "101033650663746117222",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/daily-weather-logger%40weatherdiaries.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open("City Air Diaries Weather Log")

# 🟦 Weather Fetching
API_KEY = "4eb98d4ed346aa423fa72bea6db5107b"
cities = ["Delhi", "Mumbai", "Bangalore", "Kolkata", "Chennai", "Ahmedabad", "Gurugram"]

def fetch_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "date": datetime.today().strftime('%Y-%m-%d'),
            "city": city,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"]
        }
    else:
        print(f"Failed to fetch for {city}")
        return None

# ✅ Google Sheet Updater
def update_gsheet(city_data):
    city = city_data["city"]
    try:
        worksheet = sheet.worksheet(city)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=city, rows="100", cols="10")

    existing_data = worksheet.get_all_records()
    df_existing = pd.DataFrame(existing_data)

    today = city_data["date"]
    if not df_existing.empty and ((df_existing["date"] == today) & (df_existing["city"] == city)).any():
        print(f"Data already exists for {city} on {today}")
        return

    new_row = pd.DataFrame([city_data])
    df_combined = pd.concat([df_existing, new_row], ignore_index=True) if not df_existing.empty else new_row

    worksheet.clear()
    set_with_dataframe(worksheet, df_combined)
    print(f"✅ Data saved for {city}")

# 🔁 Loop through cities
for city in cities:
    result = fetch_weather(city)
    if result:
        update_gsheet(result)
