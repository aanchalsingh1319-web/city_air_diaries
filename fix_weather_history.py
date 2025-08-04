import pandas as pd

# Load the malformed CSV (wrong column order)
df = pd.read_csv("weather_history.csv", header=None)

# Rename columns based on what they *actually* contain
df.columns = ["city", "date", "temperature", "humidity", "wind_speed", "description"]

# Reorder to the correct format
df_fixed = df[["date", "city", "temperature", "humidity", "wind_speed", "description"]]

# Save to the same file (or use 'weather_history_fixed.csv' if you want backup)
df_fixed.to_csv("weather_history.csv", index=False)

print("✅ weather_history.csv fixed successfully.")