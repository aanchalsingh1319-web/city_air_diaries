print("Welcome to City Air Diaries Project")

###Load and Explore the AQI Data

import pandas as pd

# Step 1: Load the dataset
df = pd.read_csv("city_day.csv")

# Step 2: Preview the first 5 rows
print("🔹 Data Preview:\n", df.head())

# Step 3: Check basic info
print("\n🔹 Data Info:")
print(df.info())

# Step 4: Check for missing values
print("\n🔹 Missing Values:\n", df.isnull().sum())

# Step 5: Convert 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Step 6: Drop rows where AQI is missing (or optionally fill with mean)
df_clean = df.dropna(subset=['AQI'])

# Optional: Reset index after drop
df_clean.reset_index(drop=True, inplace=True)

# Step 7: Filter only the important columns for now
df_filtered = df_clean[['Date', 'City', 'AQI', 'AQI_Bucket', 'PM2.5', 'PM10', 'NO2', 'CO']]
df_filtered.to_csv("clean_aqi_data.csv", index=False)

# Step 8: Preview cleaned data
print("\n🔹 Cleaned Data Preview:")
print(df_filtered.head())

# Step 9: Number of unique cities
print("\n🔹 Cities Available:", df_filtered['City'].nunique())
print(df_filtered['City'].unique())

##Analyze AQI Trends for a City
##Let’s pick Delhi and plot its AQI over time

import matplotlib.pyplot as plt
import seaborn as sns

# Step 10: Filter for Delhi
delhi_df = df_filtered[df_filtered['City'] == 'Delhi']

# Step 11: Plot AQI over time
plt.figure(figsize=(12,6))
sns.lineplot(data=delhi_df, x='Date', y='AQI', color='crimson')
plt.title("Delhi AQI Over Time", fontsize=16)
plt.xlabel("Date")
plt.ylabel("Air Quality Index")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


##Compare Cities by AQI

# Step 12: Choose 4 cities for comparison
cities = ['Delhi', 'Mumbai', 'Kolkata', 'Chennai']
compare_df = df_filtered[df_filtered['City'].isin(cities)]

# Step 13: Boxplot to compare distributions
plt.figure(figsize=(10,5))
sns.boxplot(data=compare_df, x='City', y='AQI')
plt.title("AQI Comparison Across Cities")
plt.show()

