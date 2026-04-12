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
    }).reset_index()
    daily_df.rename(columns={"cnt_day": "total_rent"}, inplace=True)
    return daily_df

def create_season_df(df):
    return df.groupby("season_day")["cnt_day"].mean().reset_index()

def create_hourly_df(df):
    return df.groupby("hr")["cnt_hour"].sum().reset_index()

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

main_df = all_df[
    (all_df["dteday"] >= str(start_date)) & 
    (all_df["dteday"] <= str(end_date))
]

# PREPARE DATA

daily_df = create_daily_rent_df(main_df)
season_df = create_season_df(main_df)
hour_df = create_hourly_df(main_df)

# DASHBOARD

st.header("Bike Sharing Dashboard 🚲")
st.subheader("Daily Rental Trend")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Penyewaan", int(daily_df["total_rent"].sum()))

with col2:
    st.metric("Rata-rata Harian", round(daily_df["total_rent"].mean(), 2))

# DAILY TREND

st.subheader("📈 Tren Penyewaan Harian")

fig, ax = plt.subplots(figsize=(14,6))
ax.plot(daily_df["dteday"], daily_df["total_rent"], marker='o')
ax.set_xlabel("Tanggal")
ax.set_ylabel("Jumlah Penyewaan")

st.pyplot(fig)

# PERTANYAAN 1: MUSIM

st.subheader("📊 Rata-rata Penyewaan per Hari Berdasarkan Musim")

fig, ax = plt.subplots(figsize=(10,6))
sns.barplot(data=season_df, x="season_day", y="cnt_day", ax=ax)

ax.set_xlabel("Musim")
ax.set_ylabel("Rata-rata Penyewaan Harian")

st.pyplot(fig)

# PERTANYAAN 2: JAM

st.subheader("⏰ Total Penyewaan Berdasarkan Jam")

peak_hour = hour_df.loc[hour_df["cnt_hour"].idxmax()]

fig, ax = plt.subplots(figsize=(12,6))
ax.plot(hour_df["hr"], hour_df["cnt_hour"], marker='o')
ax.scatter(peak_hour["hr"], peak_hour["cnt_hour"])
ax.set_xlabel("Jam")
ax.set_ylabel("Total Penyewaan")
ax.set_xticks(range(0,24))
ax.grid(True)

st.pyplot(fig)

# INSIGHT

st.subheader("Insight")

st.write("""
### Pertanyaan 1: Bagaimana perbedaan rata-rata jumlah penyewaan sepeda per hari pada setiap musim dalam periode tahun 2011-2012?
- Terdapat perbedaan rata-rata penyewaan sepeda pada setiap musim.
- Musim ke-3 memiliki rata-rata penyewaan tertinggi (5644.303191), sedangkan musim ke-1 terendah (2604.132597).
- Hal ini menunjukkan bahwa kondisi musim memengaruhi minat pengguna dalam bersepeda.

### Pertanyaan 2: Pada jam berapa terjadi jumlah penyewaan sepeda tertinggi berdasarkan total penyewaan per jam dalam periode 2011-2012?
- Penyewaan sepeda tidak merata sepanjang hari.
- Puncak penyewaan terjadi pada dua periode utama, yaitu pagi hari sekitar pukul 08.00 dengan total sekitar 261.001 penyewaan, dan sore hari sekitar pukul 17.00 dengan total tertinggi mencapai lebih dari 336.860 penyewaan.
- Aktivitas ini menunjukkan penggunaan sepeda sebagai sarana transportasi kerja/sekolah.
""")

st.caption("Dashboard by Naomi Yunika Aulia")

