import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np

sns.set(style='dark')

# Load dataset
day_df = pd.read_csv("dashboard/day_cleaned.csv")
hour_df = pd.read_csv("dashboard/hour_cleaned.csv")

day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])


# sidebar untuk filtering tanggal
st.sidebar.image("dashboard/img/logo.png")
start_date, end_date = st.sidebar.date_input(
    label='Rentang Waktu', 
    min_value=hour_df['dteday'].min(), 
    max_value=hour_df['dteday'].max(),
    value=[hour_df['dteday'].min(), hour_df['dteday'].max()]
)

# filter tanggal
day_filtered = day_df[(day_df['dteday'] >= pd.to_datetime(start_date)) & 
                      (day_df['dteday'] <= pd.to_datetime(end_date))]

# filter jam
hour_filtered = hour_df[(hour_df['dteday'] >= pd.to_datetime(start_date)) & 
                        (hour_df['dteday'] <= pd.to_datetime(end_date))]

st.header('Dashboard Sewa Sepeda 🚴')

col1, col2, col3 = st.columns(3)

# Buat jumlah total yang menampilkan pelanggan casual
with col1:
    total_casual = day_filtered['casual'].sum()
    st.metric(label="Total Pengguna Casual", value=total_casual)

# Buat jumlah total yang menampilkan pelanggan registered
with col2:
    total_registered = day_filtered['registered'].sum()
    st.metric(label="Total Pengguna Register", value=total_registered)
   
# Buat jumlah total yang menampilkan total pelanggan  
with col3:
    total_rent = day_filtered['cnt'].sum()
    st.metric(label="Total Pengguna", value=total_rent)
    
# 1. visualisasi line plot penyewaan sepeda harian
st.subheader("Tren Penyewaan Sepeda Harian (2011-2012)")
plt.figure(figsize=(10, 5))
sns.lineplot(x='dteday', y='cnt', data=day_filtered)
plt.xlabel("Tanggal")
plt.ylabel("Jumlah Penyewaan")
plt.title("Tren Penyewaan Sepeda Harian")
st.pyplot(plt)

# 2. visualisasi bar plot total penyewaan per bulan
monthly_trend = day_df.groupby(['yr', 'mnth'])['cnt'].sum().reset_index()
monthly_trend['yr'] = monthly_trend['yr'].map({0: 2011, 1: 2012})
pivot_trend = monthly_trend.pivot(index='mnth', columns='yr', values='cnt')

fig, ax = plt.subplots(figsize=(10, 5))
bar_width = 0.4
x_indexes = np.arange(len(pivot_trend.index))

ax.bar(x_indexes - bar_width/2, pivot_trend[2011], width=bar_width, label='2011', color='blue')
ax.bar(x_indexes + bar_width/2, pivot_trend[2012], width=bar_width, label='2012', color='orange')

st.subheader("Tren Penyewaan Sepeda Bulanan (2011-2012)")

ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Penyewaan Sepeda")
ax.set_title("Tren Penyewaan Sepeda Tiap Bulan (2011-2012)")
ax.set_xticks(x_indexes)
ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'])
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

st.pyplot(fig)

# 3. Rata rata penyewaan per jam menggunakan line lpoplot
hourly_rentals = hour_filtered.groupby('hr')['cnt'].mean()

fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(x=hourly_rentals.index, y=hourly_rentals.values, marker='o', linestyle='-', ax=ax)

# Tambahkan judul dan label
st.subheader("Rata-rata Penyewaan Sepeda per Jam")
ax.set_xlabel('Jam', fontsize=12)
ax.set_ylabel('Rata-rata Penyewaan Sepeda', fontsize=12)
ax.set_xticks(range(0, 24))
st.pyplot(fig)

# 4. Membuat bar chart untuk visualisasi per musim berdasarkan day_filtered
seasonal_rentals_filtered = day_filtered.groupby('season')['cnt'].mean().sort_values(ascending=False)

st.subheader("Rata-rata Penyewaan Sepeda berdasarkan Musim dan Cuaca")

col1, col2 = st.columns(2)
with col1:
    plt.figure(figsize=(8, 5))
    colors_ = ["#D3D3D3", "#D3D3D3", "#72BCD4", "#D3D3D3"]

    sns.barplot(
        x=seasonal_rentals_filtered.index,
        y=seasonal_rentals_filtered.values,
        palette=colors_
    )
    plt.title('Rata-rata Penyewaan Sepeda Berdasarkan Musim', fontsize=14)
    plt.xlabel('Musim', fontsize=12)
    plt.ylabel('Rata-rata Penyewaan Sepeda', fontsize=12)
    plt.xticks(ticks=[0, 1, 2, 3], labels=['Spring', 'Summer', 'Fall', 'Winter']) 
    st.pyplot(plt)

with col2:
    weather_rentals = day_filtered.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        x=weather_rentals.index,
        y=weather_rentals.values,
        palette=colors_
    )

    plt.title('Rata-rata Penyewaan Sepeda per Cuaca', fontsize=14)
    plt.xlabel('Kondisi Cuaca', fontsize=12)
    plt.ylabel('Rata-rata Penyewaan Sepeda', fontsize=12)
    plt.xticks(ticks=[0, 1, 2, 3], labels=['Clear', 'Mist', 'Light Snow', 'Heavy Rain'])  # Ubah label sesuai dengan data

    st.pyplot(plt)

# visualisasi hasil clustering berdasarkan kategori
day_filtered['dteday'] = pd.to_datetime(day_filtered['dteday'])
day_filtered['year'] = day_filtered['dteday'].dt.year
day_filtered['week'] = day_filtered['dteday'].dt.isocalendar().week

weekly_df = day_filtered.groupby(['year', 'week'])['cnt'].sum().reset_index()
bin_edges = [weekly_df['cnt'].min(), weekly_df['cnt'].quantile(0.33), weekly_df['cnt'].quantile(0.66), weekly_df['cnt'].max()]
bin_labels = ['Sepi', 'Sedang', 'Ramai']
weekly_df['category'] = pd.cut(weekly_df['cnt'], bins=bin_edges, labels=bin_labels, include_lowest=True)
colors = {'Sepi': 'red', 'Sedang': 'orange', 'Ramai': 'green'}
st.subheader('Kategori Jumlah Penyewaan sepeda tiap Minggu')

fig, ax = plt.subplots(figsize=(12, 6))

for year in weekly_df['year'].unique():
    subset = weekly_df[weekly_df['year'] == year]
    for i in range(len(subset)):
        ax.plot(subset.iloc[i]['week'], subset.iloc[i]['cnt'],
                 marker='o', linestyle='-', color=colors[subset.iloc[i]['category']], alpha=0.8)

ax.set_title('Jumlah Penyewaan Sepeda per Minggu dengan Kategori')
ax.set_xlabel('Minggu ke-')
ax.set_ylabel('Jumlah Penyewaan Sepeda')
ax.grid(True, linestyle='--', alpha=0.6)


st.pyplot(fig)
st.markdown("### Keterangan")
st.markdown("🟥 Sepi")
st.markdown("🟨 Sedang")
st.markdown("🟩 Ramai")

st.caption('Copyright (c) rifdahhr 2025')