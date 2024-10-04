import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib

# Set styling for seaborn and streamlit options
sns.set(style='dark')

# DataAnalyzer class
class DataAnalyzer:
    def __init__(self, df):
        self.df = df

    def create_daily_orders_df(self):
        daily_orders_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "order_id": "nunique",
            "payment_value": "sum"
        })
        daily_orders_df = daily_orders_df.reset_index()
        daily_orders_df.rename(columns={
            "order_id": "order_count",
            "payment_value": "revenue"
        }, inplace=True)
        
        return daily_orders_df
    
    def create_sum_spend_df(self):
        sum_spend_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "payment_value": "sum"
        })
        sum_spend_df = sum_spend_df.reset_index()
        sum_spend_df.rename(columns={
            "payment_value": "total_spend"
        }, inplace=True)

        return sum_spend_df

    def create_sum_order_items_df(self):
        sum_order_items_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
        sum_order_items_df.rename(columns={
            "product_id": "product_count"
        }, inplace=True)
        sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

        return sum_order_items_df

    def review_score_df(self):
        review_scores = self.df['review_score'].value_counts().sort_values(ascending=False)
        most_common_score = review_scores.idxmax()

        return review_scores, most_common_score

    def create_bystate_df(self):
        bystate_df = self.df.groupby(by="customer_state").customer_id.nunique().reset_index()
        bystate_df.rename(columns={
            "customer_id": "customer_count"
        }, inplace=True)
        most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
        bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

        return bystate_df, most_common_state

    def create_order_status(self):
        order_status_df = self.df["order_status"].value_counts().sort_values(ascending=False)
        most_common_status = order_status_df.idxmax()

        return order_status_df, most_common_status


# BrazilMapPlotter class
class BrazilMapPlotter:
    def __init__(self, data, plt, mpimg, urllib, st):
        self.data = data
        self.plt = plt
        self.mpimg = mpimg
        self.urllib = urllib
        self.st = st

    def plot(self):
        brazil = self.mpimg.imread(self.urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'),'jpg')
        ax = self.data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", figsize=(10,10), alpha=0.3,s=0.3,c='maroon')
        self.plt.axis('off')
        self.plt.imshow(brazil, extent=[-73.98283055, -33.8,-33.75116944,5.4])
        self.st.pyplot()


# Dashboard implementation starts here
# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("D:/Sampoerna University/Boothcamp/Bangkit Academy 2024 By Google, GoTo, Tokopedia, Traveloka - Machine Learning Learning Path/Proyek Analisis Data - Belajar Analisis Data dengan Python - Dicoding/dashboard/df.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv('D:/Sampoerna University/Boothcamp/Bangkit Academy 2024 By Google, GoTo, Tokopedia, Traveloka - Machine Learning Learning Path/Proyek Analisis Data - Belajar Analisis Data dengan Python - Dicoding/dashboard/geolocation_dataset.csv')

# **DEBUGGING: Print column names to inspect the data**
st.write("**Inspecting Columns in geolocation dataset:**")
st.write(geolocation.columns)  # Display the column names

# **Fixing the missing columns issue**: Check if 'customer_unique_id' or 'customer_id' exists
if 'customer_unique_id' in geolocation.columns:
    # If 'customer_unique_id' exists, use it
    data = geolocation.drop_duplicates(subset='customer_unique_id')
elif 'customer_id' in geolocation.columns:
    # If 'customer_unique_id' does not exist but 'customer_id' exists, use it
    data = geolocation.drop_duplicates(subset='customer_id')
else:
    # If neither 'customer_unique_id' nor 'customer_id' exist, stop execution and display an error
    st.error("Neither 'customer_unique_id' nor 'customer_id' exist in the geolocation data.")
    st.stop()  # This will stop the script execution

# Convert datetime columns to datetime objects
for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

# Get the minimum and maximum order approval dates
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(' ')
    with col2:
        st.image("D:\Sampoerna University\Boothcamp\Bangkit Academy 2024 By Google, GoTo, Tokopedia, Traveloka - Machine Learning Learning Path\Proyek Analisis Data - Belajar Analisis Data dengan Python - Dicoding\dashboard\logo-garuda.png", width=100)
    with col3:
        st.write(' ')

    # Date Range input for filtering the data
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Filter main DataFrame based on the selected date range
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

# Initialize DataAnalyzer and BrazilMapPlotter objects
function = DataAnalyzer(main_df)

# We only reach this point if the 'data' variable was defined successfully
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)  # This line should work now

# Process DataFrames
daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Define your Streamlit app
st.title("E-Commerce Public Data Analysis")

# Add text or descriptions
st.write("**This is a dashboard for analyzing E-Commerce public data.**")

# Daily Orders Delivered Section
st.subheader("Daily Orders Delivered")
col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = daily_orders_df["revenue"].sum()
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    x=daily_orders_df["order_approved_at"],
    y=daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Add other sections similarly...

# Geolocation Section - Map
st.subheader('Customer Geolocation in Brazil')
map_plot.plot()