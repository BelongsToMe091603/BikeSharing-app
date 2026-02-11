import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from babel.numbers import format_currency
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import time

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "instant": "nunique",
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "instant": "record_index",
        "cnt": "count_of_total_rental_bikes"
    }, inplace=True)
    return daily_orders_df

def create_rental_by_hour(df):
    rental_by_hour = df.groupby('hr').cnt.mean().sort_values(ascending=False).reset_index()
    rental_by_hour['hr'] = rental_by_hour['hr'].astype(str)
    return rental_by_hour

def create_rental_by_month(df):
    rental_by_month = df.groupby('mnth').cnt.mean().sort_values(ascending=False).reset_index()
    rental_by_month['mnth'] = rental_by_month['mnth'].astype(str)
    return rental_by_month

def create_avg_users_active(df):
    avg_users_per_hour = (df.groupby("hr")[["casual", "registered"]].mean().reset_index())
    avg_users_per_hour["casual_ratio"] = (
        avg_users_per_hour["casual"] /
        (avg_users_per_hour["casual"] + avg_users_per_hour["registered"])
    )
    return avg_users_per_hour

def create_avg_users_active_by_month(df):
    avg_users_per_month = (df.groupby("mnth")[["casual", "registered"]].mean().reset_index())
    avg_users_per_month["casual_ratio"] = (
        avg_users_per_month["casual"] /
        (avg_users_per_month["casual"] + avg_users_per_month["registered"])
    )
    return avg_users_per_month

def bike_recommendation(df):
    # Rule 1: Cuaca buruk langsung TIDAK
    if df["weathersit"] >= 3:
        return "TIDAK"
    
    # Rule 2: Temperatur tidak ideal
    if df["temp"] < 0.3 or df["temp"] > 0.7:
        return "TIDAK"
    
    # Rule 3: Kelembapan terlalu tinggi
    if df["hum"] > 0.8:
        return "TIDAK"
    
    # Rule 4: Angin terlalu kencang
    if df["windspeed"] > 0.4:
        return "TIDAK"
    
    # Jika lolos semua rule
    return "YA"

# Load cleaned data
hours_df = pd.read_csv("dashboard/all_data.csv")

datetime_columns = ["dteday"]
hours_df.sort_values(by="dteday", inplace=True)
hours_df.reset_index(inplace=True)

for column in datetime_columns:
    hours_df[column] = pd.to_datetime(hours_df[column])

hours_df["bike_recommendation"] = hours_df.apply(
    bike_recommendation, axis=1
)

# Filter data
min_data = hours_df["dteday"].min()
max_data = hours_df["dteday"].max()

with st.sidebar:
    
    st.markdown(
        """
        <h1 style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:64px;">🚴</span>
        </h1>
        """,
        unsafe_allow_html=True
    )
    
    # add_selectbox = st.sidebar.selectbox(
    #     "How would you like to be contacted?",
    #     ("Email", "Home phone", "Mobile phone")
    # )

    # add_radio = st.radio(
    #     "Choose a shipping method",
    #     ("Standard (5-15 days)", "Express (2-5 days)")
    # )

    # Mengambil start_date & end_date dari data_input tanggal
    start_date, end_date = st.date_input(
        label='Select Date Range', 
        min_value=min_data,
        max_value=max_data,
        value=[min_data, max_data]
    )

    start_hour, end_hour = st.slider(
        label="Select Hour Range", 
        min_value=0,
        max_value=23,
        value=(0, 23)
    )

# main_df = hours_df[(hours_df["dteday"] >= str(start_date)) &
#                    (hours_df["dteday"] <= str(end_date))]

main_df = hours_df[
    (hours_df["dteday"] >= pd.to_datetime(start_date)) &
    (hours_df["dteday"] <= pd.to_datetime(end_date)) &
    (hours_df["hr"] >= start_hour) &
    (hours_df["hr"] <= end_hour)
]

# Menyiapkan berbagai dataframe
daily_orders_df = create_daily_orders_df(main_df)
rental_by_hour = create_rental_by_hour(main_df)
rental_by_month = create_rental_by_month(main_df)
avg_users_active = create_avg_users_active(main_df)
avg_users_active_by_month = create_avg_users_active_by_month(main_df)

# 
with st.spinner("Wait for it...", show_time=True):
    time.sleep(1)

st.header('Bike Sharing :material/pedal_bike:')

st.subheader('Daily Rental') # 
col1, col2, col3 = st.columns(3)

with col1:
    total_rental = daily_orders_df.count_of_total_rental_bikes.sum()
    st.metric("Total Rentals", value=total_rental)  

with col2:
    casual_users = daily_orders_df.casual.sum()
    st.metric("Casual Users", value=casual_users)  

with col3:
    registered_users = daily_orders_df.registered.sum()
    st.metric("Registered Users", value=registered_users)  

st.subheader("High and Low Demand of Bicycle Rental based Time") # Grafik tertinggi dan terendah
col1, col2 = st.columns(2)

with col1:
    high_rental = rental_by_hour.loc[rental_by_hour.cnt.idxmax(), 'hr']
    st.metric("Peak Hour", value=f"{int(high_rental):02d}:00")  

with col2:
    low_rental = rental_by_hour.loc[rental_by_hour.cnt.idxmin(), 'hr']
    st.metric("Low Demand Hour", value=f"{int(low_rental):02d}:00")  

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#60B5FF", "#AFDDFF", "#AFDDFF", "#AFDDFF", "#AFDDFF"]

sns.barplot(
    x="cnt", 
    y="hr", 
    hue="hr",
    data=rental_by_hour.head(5), 
    palette=colors, 
    legend=False,
    ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total of Rental", fontsize=30)
ax[0].set_title("High Rental based Time", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(
    x="cnt", 
    y="hr", 
    hue="hr",
    data=rental_by_hour.sort_values(by="cnt", ascending=True).head(5), 
    palette=colors, 
    legend=False,
    ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Total of Rental", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Low Rental based Time", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

col1, col2 = st.columns(2)

with col1:
    casual_ratio = avg_users_active.casual_ratio.max()
    st.metric("Casual ratio", value=f"{casual_ratio:.2%}")

with col2:
    hour = avg_users_active.loc[avg_users_active.casual_ratio.idxmax(), 'hr']
    st.metric("Highest Casual Ratio", value=f"{int(hour):02d}:00")

fig, ax = plt.subplots(figsize=(35,15))

plt.plot(
    avg_users_active["hr"],
    avg_users_active["casual"],
    marker="o",
    linewidth=4,              # garis lebih tebal
    markersize=10,            # marker lebih besar
    label="Casual Users",
)

plt.plot(
    avg_users_active["hr"],
    avg_users_active["registered"],
    marker="o",
    linewidth=4,              # garis lebih tebal
    markersize=10,            # marker lebih besar
    label="Registered Users"
)

plt.title("Average Casual vs Registered Users by Hour", fontsize=50)
plt.xlabel("Hour", fontsize=35)
plt.ylabel("Average Number of Users", fontsize=35)
plt.xticks(range(start_hour, end_hour+1), rotation=45, fontsize=25)
plt.yticks(fontsize=25)

# 🔑 format jam jadi 2 angka desimal
plt.gca().xaxis.set_major_formatter(
    FuncFormatter(lambda x, _: f"{x:02d}:00")
)

plt.legend(
    fontsize=30,          # ukuran teks legend
    title="User Type",
    title_fontsize=32,
    loc="upper right"
)
plt.grid(alpha=0.3)

st.pyplot(fig)


# Month
st.subheader("Monthly Rental")
col1, col2 = st.columns(2)

month_map = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

with col1:
    peak_month_num = int(rental_by_month.loc[rental_by_month.cnt.idxmax(), 'mnth'])
    peak_month = month_map[peak_month_num]
    st.metric("Peak Month", value=peak_month)  

with col2:
    low_month_num = int(rental_by_month.loc[rental_by_month.cnt.idxmin(), 'mnth'])
    low_month = month_map[low_month_num]
    st.metric("Low Demand Month", value=low_month)  

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#60B5FF", "#AFDDFF", "#AFDDFF", "#AFDDFF", "#AFDDFF"]

sns.barplot(
    x="cnt", 
    y="mnth", 
    hue="mnth",
    data=rental_by_month.head(5), 
    palette=colors, 
    legend=False,
    ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total of Rental", fontsize=30)
ax[0].set_title("High Rental based Month", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(
    x="cnt", 
    y="mnth", 
    hue="mnth",
    data=rental_by_month.sort_values(by="cnt", ascending=True).head(5), 
    palette=colors, 
    legend=False,
    ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Total of Rental", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Low Rental based Month", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

col1, col2 = st.columns(2)

with col1:
    casual_ratio_by_month = avg_users_active_by_month.casual_ratio.max()
    st.metric("Casual ratio", value=f"{casual_ratio_by_month:.2%}")

with col2:
    month = avg_users_active_by_month.loc[avg_users_active_by_month.casual_ratio.idxmax(), 'mnth']
    st.metric("Highest Casual Ratio", value=f"{month_map[month]}")

monthly_df = (
    main_df
    .groupby(main_df['dteday'].dt.month)
    .agg(cnt=('cnt', 'sum'))
    .reset_index()
)

fig, ax = plt.subplots(figsize=(35,15))

plt.plot(
    avg_users_active_by_month["mnth"],
    avg_users_active_by_month["casual"],
    marker="o",
    linewidth=4,              # garis lebih tebal
    markersize=10, 
    label="Casual Users"
)

plt.plot(
    avg_users_active_by_month["mnth"],
    avg_users_active_by_month["registered"],
    marker="o",
    linewidth=4,              # garis lebih tebal
    markersize=10, 
    label="Registered Users"
)

plt.title("Average Casual vs Registered Users by Month", fontsize=50)
plt.xlabel("Month", fontsize=35)
plt.ylabel("Average Number of Users", fontsize=35)
plt.xticks(
    range(start_date.month, end_date.month+1), 
    [month_map[i] for i in range(start_date.month, end_date.month+1)], 
    rotation=45, 
    fontsize=25
)
plt.yticks(fontsize=25)

plt.legend(
    fontsize=30,          # ukuran teks legend
    title="User Type",
    title_fontsize=32,
    loc="upper right"
)
plt.grid(alpha=0.3)
st.pyplot(fig)

# Recommendation
st.header("Recommended Rental Days")
col1, col2 = st.columns(2)

tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
with tab1:
    st.subheader("Bike Recommendation Count")

    fig, ax = plt.subplots(figsize=(14,6))

    sns.countplot(
        x="bike_recommendation",
        data=hours_df,
        hue="bike_recommendation",     # 🔑 untuk palette
        palette={"YA": "green", "TIDAK": "red"},
        legend=False,
        ax=ax
    )

    ax.set_title("Bike Recommendation Based on Weather Rules", fontsize=18)
    ax.set_xlabel("Recommendation", fontsize=14)
    ax.set_ylabel("Total Observations", fontsize=14)
    ax.tick_params(axis='both', labelsize=12)
    # ax.set_yticks(range(start_date.day, end_date.day))

    # 🔑 Tambahkan jumlah di atas bar
    for p in ax.patches:
        ax.annotate(
            f"{int(p.get_height())}",
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center',
            va='bottom',
            fontsize=12,
            fontweight='bold'
        )

    st.pyplot(fig)

with tab2:
    st.subheader("Bike Recommendation Data")
    st.dataframe(hours_df[[
        "dteday", "hr", "weathersit", "temp", "hum",
        "windspeed", "bike_recommendation"
    ]].sort_values(by=["dteday", "hr"], ascending=True)
    )

# scatter-plot
daily_recommendation = (
    hours_df
    .groupby("dteday")["bike_recommendation"]
    .apply(lambda x: "YA" if (x == "YA").mean() > 0.6 else "TIDAK")
    .reset_index()
)

fig, ax = plt.subplots(figsize=(14,6))
sns.scatterplot(
    data=hours_df,
    x="temp",
    y="cnt",
    hue="bike_recommendation",
    palette={"YA": "green", "TIDAK": "red"},
    alpha=0.6
)
plt.title("Bike Recommendation Based on Temperature", fontsize=16)
plt.xlabel("Temperature (Normalized)", fontsize=12)
plt.ylabel("Total Bike Rentals", fontsize=12)
plt.legend(title="Recommendation")
plt.grid(alpha=0.3)
st.pyplot(fig)

#
fig, ax = plt.subplots(figsize=(14,6))
sns.scatterplot(
    data=hours_df,
    x="hum",
    y="windspeed",
    hue="bike_recommendation",
    palette={"YA": "green", "TIDAK": "red"},
    alpha=0.6
)
plt.title("Bike Recommendation Based on Humidity & Wind Speed", fontsize=16)
plt.xlabel("Humidity", fontsize=12)
plt.ylabel("Wind Speed", fontsize=12)
plt.legend(title="Recommendation")
plt.grid(alpha=0.3)
st.pyplot(fig)

#
fig, ax = plt.subplots(figsize=(14,6))
sns.scatterplot(
    x="temp",
    y="hum",
    hue="bike_recommendation",
    data=hours_df,
    alpha=0.5
)

plt.title("Bike Recommendation Scatter Overview")
st.pyplot(fig)