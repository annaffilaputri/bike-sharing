import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Membuat helper function
def create_daily_rent_df(df):
    daily_rent_df = df.resample(rule='D', on='dteday').agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    daily_rent_df = daily_rent_df.reset_index()
    daily_rent_df.rename(columns={
        "casual": "non_member",
        "registered": "member",
        "cnt": "rent_count"
    }, inplace=True)

    return daily_rent_df

def create_byseason_df(df):
    byseason_df = df.groupby(by="season").cnt.sum()
    byseason_df = byseason_df.to_frame().reset_index()
    return byseason_df

def create_byweather_df(df):
    byweather_df = df.groupby(by="weathersit").cnt.sum()
    byweather_df = byweather_df.to_frame().reset_index()
    return byweather_df

def create_byworkingday_df(df):
    byworkingday_df = df.groupby(by="workingday").cnt.sum()
    return byworkingday_df

def create_byday_df(df):
    byday_df = df.groupby(by="weekday").cnt.sum()
    byday_df = byday_df.to_frame().reset_index()
    return byday_df

def create_byhour_df(df):
    byhour_df = df.groupby(by="hr").cnt.sum()
    byhour_df = byhour_df.to_frame().reset_index()
    return byhour_df

def create_bymembership_df(df):
    non_member = pd.Series(df["casual"].sum())
    member = pd.Series(df["registered"].sum())
    bymembership_df = pd.concat([non_member, member])
    return bymembership_df

def create_rent_history(df):
    df['Month_Year'] = df['dteday'].dt.to_period('M')
    rent_history = df.groupby(by="Month_Year").cnt.sum()
    rent_history = rent_history.to_frame().reset_index()
    return rent_history

# Load berkas day_df.csv
day_df = pd.read_csv("day_cleaned.csv")
hour_df = pd.read_csv("hour_cleaned.csv")

# Memastikan kolom bertipe date time untuk filter
datetime_columns = ["dteday"]
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)

for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])

# Membuat filter dengan widget date input
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

# Mengatur content pada sidebar
with st.sidebar:
    # Menambahkan logo
    st.image("bike_sharing_logo.png")

    # Mengambil start_date & end_date dati date_input
    start_date, end_date = st.date_input(
        label='Range Time',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Menambahkan identitas diri
    st.markdown("Dibuat oleh An Naffila Putri Prasari  \n [Naffila's LinkedIn](https://linkedin.com/in/annaffilaputri)")

# Data yang telah difilter disimpan dalam main_df dan sec_df
main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]
sec_df = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                (hour_df["dteday"] <= str(end_date))]

# Memanggil helper function
daily_rent_df = create_daily_rent_df(main_df)
byseason_df = create_byseason_df(main_df)
byweather_df = create_byweather_df(main_df)
byworkingday_df = create_byworkingday_df(main_df)
byday_df = create_byday_df(main_df)
byhour_df = create_byhour_df(sec_df)
bymembership_df = create_bymembership_df(main_df)
rent_history = create_rent_history(main_df)

# ''' Melengkapi Dashboard dengan Berbagai Visualisasi Data'''
# Menambahkan header
st.header('Bike Sharing Dashboard :bike:')

# Menambahkan informasi terkait daily orders
st.subheader('Daily Rent')

col1, col2 , col3= st.columns(3)

with col1:
    total_rent = daily_rent_df.rent_count.sum()
    st.metric("Total rent", value=total_rent)

with col2:
    total_member = daily_rent_df.member.sum()
    st.metric("Member", value=total_member)

with col3:
    total_nonmember = daily_rent_df.non_member.sum()
    st.metric("Non member", value=total_nonmember)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_rent_df["dteday"],
    daily_rent_df["rent_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# Menampilkan informasi tentang faktor-faktor yang mempengaruhi peminjaman sepeda
st.subheader("Factors influencing bicycle rental")

#fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(50, 70))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

fig, ax1 = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))

sns.barplot(x="season", y="cnt", data=byseason_df.sort_values(by="cnt", ascending=False), palette=colors, ax=ax1[0])
ax1[0].set_ylabel(None)
ax1[0].set_xlabel(None)
ax1[0].set_title("Number of Bike Rental by Seasons", loc="center", fontsize=27)
ax1[0].tick_params(axis='y', labelsize=18)
ax1[0].tick_params(axis='x', labelsize=18)

plt.pie(byworkingday_df, colors=["#d6614f", "#85b7de"], labels=["Holiday", "Working Day"],
        autopct='%1.1f%%', pctdistance=0.85
)
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)
ax1[1].set_title("Bike Rental on Working Day vs. Holiday", loc="center", fontsize=20)
ax1[1].set_ylabel(None)
ax1[1].set_xlabel(None)
ax1[1].tick_params(axis='x', labelsize=18)
st.pyplot(fig)

fig, ax2 = plt.subplots(figsize=(16, 8))
sns.barplot(x="cnt", y="weathersit", data=byweather_df.sort_values(by="cnt", ascending=False), palette=colors, orient='h')
ax2.set_ylabel(None)
ax2.set_xlabel(None)
ax2.yaxis.set_label_position("left")
ax2.yaxis.tick_left()
ax2.set_title("Number of Bike Rental by Weather", loc="center", fontsize=45)
ax2.tick_params(axis='y', labelsize=25)
ax2.tick_params(axis='x', labelsize=25)
st.pyplot(fig)

# Menampilkan waktu peminjaman sepeda tertinggi dan terendah
st.subheader("Highest bicycle borrowing time")

fig, ax3 = plt.subplots(figsize=(16, 8))
sns.barplot(
    y = "weekday",
    x = "cnt",
    data = byday_df.sort_values(by="cnt", ascending=False),
    palette = colors
)
plt.title("Number of Bike Rental by Day", loc="center", fontsize=27)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='y', labelsize=18)
plt.tick_params(axis='x', labelsize=18)
st.pyplot(fig)

fig, ax4 = plt.subplots(figsize=(16, 8))
sns.lineplot(
    y = "cnt",
    x = "hr",
    data = byhour_df
)
plt.title("Number of Bike Rental by Hour", loc="center", fontsize=27)
plt.ylabel(None)
plt.xlabel(None)
plt.xticks(np.arange(min(byhour_df.hr), max(byhour_df.hr)+1, 1.0))
plt.tick_params(axis='y', labelsize=18)
plt.tick_params(axis='x', labelsize=18)
st.pyplot(fig)

# Menampilkan perbandingan antara jumlah pengguna biasa dengan pengguna terdaftar
st.subheader("Number of Bike Rental by Membership")
fig, ax5 = plt.subplots(figsize=(16, 8))
plt.pie(bymembership_df, colors=["#85b7de", "#7ae673"], labels=["Casual", "Registered"],
        autopct='%1.1f%%', pctdistance=0.85
)

centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

plt.title("Number of Casual vs. Registered Users", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

# Menampilkan histori peminjaman sepeda pada rentang tahun 2011-2012
st.subheader("History of Bike Rental per Month")
fig, ax6 = plt.subplots(figsize=(16, 8))
sns.lineplot(
    y = rent_history["cnt"],
    x = rent_history["Month_Year"].astype(str),
)
plt.title("Number of Bike Rental per Month", loc="center", fontsize=27)
plt.ylabel(None)
plt.xlabel(None)
plt.xticks(rotation=90)
st.pyplot(fig)