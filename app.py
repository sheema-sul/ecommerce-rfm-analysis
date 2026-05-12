import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# background
st.markdown(
    """
    <style>
    .stApp {
        background-color: #dbeafe;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# page title
st.title("E-Commerce Customer Behavior & Retention Analysis using RFM Segmentation")


# load data
df = pd.read_csv("data/cleaned_ecommerce_data.csv")


# convert data
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])


# create total price
if "TotalPrice" not in df.columns:
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]


#KPI metrics
total_revenue = df["TotalPrice"].sum()
total_customers = df["CustomerID"].nunique()
total_orders = df["InvoiceNo"].nunique()


# display kpi cards
col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Customers", total_customers)
col3.metric("Total Orders", total_orders)


# RFM ANALYSIS

reference_date = df["InvoiceDate"].max()

rfm = df.groupby("CustomerID").agg({
    "InvoiceDate": lambda x: (reference_date - x.max()).days,
    "InvoiceNo": "nunique",
    "TotalPrice": "sum"
})

rfm.columns = ["Recency", "Frequency", "Monetary"]


# RFM scoring
rfm["R_Score"] = pd.qcut(
    rfm["Recency"],
    5,
    labels=[5,4,3,2,1]
).astype(str)

rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    5,
    labels=[1,2,3,4,5]
).astype(str)

rfm["M_Score"] = pd.qcut(
    rfm["Monetary"],
    5,
    labels=[1,2,3,4,5]
).astype(str)


# customer segmentation
def segment_customer(row):

    if row["R_Score"] == "5" and row["F_Score"] == "5":
        return "Champions"

    elif row["F_Score"] in ["4", "5"]:
        return "Loyal Customers"

    elif row["R_Score"] == "5":
        return "Recent Customers"

    elif row["R_Score"] in ["1", "2"]:
        return "At Risk"

    else:
        return "Regular Customers"


rfm["Segment"] = rfm.apply(segment_customer, axis=1)


# CHARTS

# Mpnthly revenue trend
st.subheader("Monthly Revenue Trend")

df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)

monthly_sales = (
    df.groupby("Month")["TotalPrice"]
    .sum()
)

fig2, ax2 = plt.subplots(figsize=(12,6))

monthly_sales.plot(color='black', ax=ax2)
j
ax2.set_xlabel("Month")
ax2.set_ylabel("Revenue")

st.pyplot(fig2)


# Top countries by revenue
st.subheader("Top Countries by Revenue")

country_revenue = (
    df.groupby("Country")["TotalPrice"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(10,6))

sns.barplot(
    x=country_revenue.values,
    y=country_revenue.index,
    color='black',
    ax=ax
)

ax.set_xlabel("Revenue")
ax.set_ylabel("Country")

st.pyplot(fig)


# Top selling products
st.subheader("Top Selling Products")

top_products = (
    df.groupby("Description")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig3, ax3 = plt.subplots(figsize=(12,6))

sns.barplot(
    x=top_products.values,
    y=top_products.index,
    color='black',
    ax=ax3
)

ax3.set_xlabel("Quantity Sold")
ax3.set_ylabel("Product")

st.pyplot(fig3)


# Customer segment distribution
st.subheader("Customer Segment Distribution")

fig4, ax4 = plt.subplots(figsize=(10,6))

sns.countplot(
    data=rfm,
    x="Segment",
    color='black',
    order=rfm["Segment"].value_counts().index,
    ax=ax4
)

plt.xticks(rotation=15)

st.pyplot(fig4)


# Revenue by segmennt
st.subheader("Revenue by Customer Segment")

segment_revenue = (
    rfm.groupby("Segment")["Monetary"]
    .sum()
    .sort_values(ascending=False)
)

fig5, ax5 = plt.subplots(figsize=(10,6))

sns.barplot(
    x=segment_revenue.index,
    y=segment_revenue.values,
    color='black',
    ax=ax5
)

plt.xticks(rotation=15)

st.pyplot(fig5)


# Top customers
st.subheader("Top 10 Customers by Revenue")

top_customers = (
    rfm.sort_values(by="Monetary", ascending=False)
    .head(10)
)

fig6, ax6 = plt.subplots(figsize=(12,6))

sns.barplot(
    x=top_customers["Monetary"],
    y=top_customers.index.astype(str),
    color='black',
    ax=ax6
)

ax6.set_xlabel("Revenue")
ax6.set_ylabel("Customer ID")

st.pyplot(fig6)


# recency distribution
st.subheader("Recency Distribution")

fig7, ax7 = plt.subplots(figsize=(10,6))

sns.histplot(
    rfm["Recency"],
    bins=30,
    color='black',
    ax=ax7
)

ax7.set_xlabel("Recency (Days)")
ax7.set_ylabel("Number of Customers")

st.pyplot(fig7)