import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_daily_rent_df(df):
    daily_df = df.resample(rule='D', on='dteday').agg({
        "cnt_day": "sum"
    })
    daily_df = daily_df.reset_index()
    daily_df.rename(columns={"cnt_day": "total_rent"}, inplace=True)
    return daily_df

def create_season_df(df):
    return df.groupby("season_day")["cnt_day"].mean().reset_index()

def create_hourly_df(df):
    return df.groupby("hr")["cnt_hour"].sum().reset_index()

def create_weather_df(df):
    return df.groupby("weathersit_day")["cnt_day"].mean().reset_index()

def create_demand_cluster(df):
    day_df = df.groupby("dteday")["cnt_day"].sum().reset_index()

    day_df["demand_level"] = pd.cut(
        day_df["cnt_day"],
        bins=[0, 2000, 5000, 9000],
        labels=["Low", "Medium", "High"]
    )
    return day_df

def create_time_category(df):
    hour_df = df.groupby("hr")["cnt_hour"].sum().reset_index()

    def time_category(x):
        if x < 6:
            return "Dini Hari"
        elif x < 12:
            return "Pagi"
        elif x < 18:
            return "Siang"
        else:
            return "Malam"

    hour_df["time_category"] = hour_df["hr"].apply(time_category)
    return hour_df

# Load cleaned data
all_df = pd.read_csv("main_data.csv")

# convert datetime
all_df["dteday"] = pd.to_datetime(all_df["dteday"])

# sort data
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)

# SIDEBAR FILTER

min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    st.title("Filter Data")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                 (all_df["dteday"] <= str(end_date))]

# PREPARE DATA

daily_df = create_daily_rent_df(main_df)
season_df = create_season_df(main_df)
hour_df = create_hourly_df(main_df)
weather_df = create_weather_df(main_df)
cluster_df = create_demand_cluster(main_df)
time_df = create_time_category(main_df)

# DASHBOARD

st.header("Bike Sharing Dashboard 🚲")
st.subheader("Daily Rental Trend")

col1, col2 = st.columns(2)

with col1:
    total_rent = daily_df["total_rent"].sum()
    st.metric("Total Penyewaan", value=total_rent)

with col2:
    avg_rent = round(daily_df["total_rent"].mean(), 2)
    st.metric("Rata-rata Harian", value=avg_rent)

# DAILY TREND

fig, ax = plt.subplots(figsize=(16,8))
ax.plot(
    daily_df["dteday"],
    daily_df["total_rent"],
    marker='o',
    linewidth=2
)

ax.set_title("Trend Penyewaan Harian", fontsize=20)
st.pyplot(fig)

# PERTANYAAN 1: MUSIM

st.subheader("Pengaruh Musim terhadap Penyewaan")

fig, ax = plt.subplots(figsize=(10,6))
sns.barplot(data=season_df, x="season_day", y="cnt_day", ax=ax)

st.pyplot(fig)

# PERTANYAAN 2: JAM

st.subheader("Pola Penyewaan Berdasarkan Jam")

fig, ax = plt.subplots(figsize=(12,6))
ax.plot(hour_df["hr"], hour_df["cnt_hour"], marker='o')

st.pyplot(fig)

# KATEGORI WAKTU

st.subheader("Pola Berdasarkan Kategori Waktu")

time_summary = time_df.groupby("time_category")["cnt_hour"].sum().reset_index()

fig, ax = plt.subplots(figsize=(10,6))
sns.barplot(data=time_summary, x="time_category", y="cnt_hour", ax=ax)

st.pyplot(fig)

# CUACA

st.subheader("Pengaruh Cuaca")

fig, ax = plt.subplots(figsize=(10,6))
sns.barplot(data=weather_df, x="weathersit_day", y="cnt_day", ax=ax)

st.pyplot(fig)

# CLUSTERING

st.subheader("Clustering Demand Level")

fig, ax = plt.subplots(figsize=(10,6))
sns.countplot(data=cluster_df, x="demand_level", ax=ax)

st.pyplot(fig)

# INSIGHT

st.subheader("Insight")

st.write("""
- Penyewaan sepeda dipengaruhi oleh musim tertentu. Penyewaan tertinggi terjadi pada musim ke 3 dan terendah pada musim ke 1.
- Terdapat jam sibuk (peak hour) pada waktu tertentu. Pagi (sekitar jam 07.00-09.00) dan Sore (sekitar jam 16.00-18.00). 
- Ini menunjukkan bahwa sepeda banyak digunakan untuk aktivitas berangkat dan pulang kerja/sekolah.
- Puncak tertinggi ada di sore hari (sekitar jam 17.00) yang menandakan bahwa mobilitas pulang kerja lebih tinggi dibanding berangkat.
- Cuaca memiliki pengaruh terhadap jumlah penyewaan.
- Clustering menunjukkan adanya tingkat permintaan: rendah, sedang, dan tinggi.
- Waktu siang dan malam cenderung memiliki aktivitas penyewaan lebih tinggi.
""")

st.caption("Dashboard by Naomi Yunika Aulia")

