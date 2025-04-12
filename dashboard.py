import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# Load and clean data
def load_data():
    df = pd.read_csv("BoCW_UP_Monthly_Data.csv")
    
    # Clean percentage columns
    percentage_cols = [
        "Registration Completion Rate",
        "Success Rate (Claims)", 
        "Renewal Rate",
        "Drop-off Rate"
    ]
    for col in percentage_cols:
        df[col] = df[col].str.replace("%", "").astype(float) / 100
    
    # Create proper date column
    df["Date"] = pd.to_datetime(
        df["Year"].astype(str) + "-" + df["Month"] + "-01",
        format="%Y-%b-%d"
    )
    return df.sort_values("Date")

df = load_data()

# Get unique years and ordered months
years = df["Year"].unique().tolist()
months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Streamlit app
st.set_page_config(layout="wide")
st.title("UP BoCW Worker Registration Dashboard")

# =====================
# Month-Year Filters (Sidebar)
# =====================
st.sidebar.header("Filters")

# Start Month-Year
start_year = st.sidebar.selectbox(
    "Start Year", 
    options=years, 
    index=0
)
start_months = df[df["Year"] == start_year]["Month"].unique()
start_month = st.sidebar.selectbox(
    "Start Month",
    options=sorted(start_months, key=lambda x: months_order.index(x)),
    index=0
)

# End Month-Year
end_year = st.sidebar.selectbox(
    "End Year", 
    options=years, 
    index=len(years)-1
)
end_months = df[df["Year"] == end_year]["Month"].unique()
end_month = st.sidebar.selectbox(
    "End Month",
    options=sorted(end_months, key=lambda x: months_order.index(x)),
    index=len(end_months)-1
)

# Convert to datetime range
start_date = datetime(start_year, months_order.index(start_month) + 1, 1)
_, last_day = calendar.monthrange(end_year, months_order.index(end_month) + 1)
end_date = datetime(end_year, months_order.index(end_month) + 1, last_day)

# Filter data
filtered_df = df[
    (df["Date"] >= pd.Timestamp(start_date)) & 
    (df["Date"] <= pd.Timestamp(end_date))
]

# =====================
# Key Metrics Cards
# =====================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        "Total Registered Workers", 
        f"{filtered_df['Total Registered Workers (End of Month)'].iloc[-1]:,}"
    )
    
with col2:
    st.metric(
        "Avg. Registration Time", 
        f"{filtered_df['Avg. Time to Register (days)'].mean():.1f} days"
    )

with col3:
    st.metric(
        "Renewal Rate", 
        f"{filtered_df['Renewal Rate'].mean():.1%}"
    )

with col4:
    st.metric(
        "Claims Success Rate", 
        f"{filtered_df['Success Rate (Claims)'].mean():.1%}"
    )

# =====================
# Time-Series Charts
# =====================
st.subheader("Trend Analysis")

# Chart 1: Total Registered Workers
fig1 = px.line(
    filtered_df,
    x="Date",
    y="Total Registered Workers (End of Month)",
    title="Total Registered Workers Over Time",
    markers=True
)
st.plotly_chart(fig1, use_container_width=True)

# Chart 2: New Registrations vs Claims
fig2 = px.bar(
    filtered_df,
    x="Date",
    y=["New Registrations", "Claims Settled"],
    title="Monthly Registrations vs Claims Settled",
    barmode="group"
)
st.plotly_chart(fig2, use_container_width=True)

# =====================
# Raw Data Table
# =====================
st.subheader("Filtered Data")
st.dataframe(
    filtered_df.style.format({
        "Registration Completion Rate": "{:.1%}",
        "Success Rate (Claims)": "{:.1%}",
        "Renewal Rate": "{:.1%}",
        "Drop-off Rate": "{:.1%}"
    }),
    height=400,
    use_container_width=True
)