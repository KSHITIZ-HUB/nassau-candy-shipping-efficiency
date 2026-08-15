
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Nassau Candy Shipping Efficiency",
    page_icon="🚚",
    layout="wide",
)

st.title("🚚 Nassau Candy Shipping Efficiency Dashboard")
st.caption("Customer-geography and shipping-performance analysis")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=True, errors="coerce")
    df["Lead Time (Days)"] = (df["Ship Date"] - df["Order Date"]).dt.days
    df["Year"] = df["Order Date"].dt.year
    df["Route"] = df["Region"].astype(str) + " → " + df["State/Province"].astype(str)
    return df

# The supplied CSV is expected in the same folder as this app.
DATA_PATH = "Nassau Candy Distributor.csv"
try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"Could not find `{DATA_PATH}`. Put the CSV in the same folder as app.py.")
    st.stop()

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")
date_min, date_max = df["Order Date"].min().date(), df["Order Date"].max().date()
date_range = st.sidebar.date_input(
    "Order date range", value=(date_min, date_max),
    min_value=date_min, max_value=date_max
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date = end_date = pd.Timestamp(date_range)

regions = st.sidebar.multiselect("Region", sorted(df["Region"].dropna().unique()), default=sorted(df["Region"].dropna().unique()))
states = st.sidebar.multiselect("State / Province", sorted(df["State/Province"].dropna().unique()))
modes = st.sidebar.multiselect("Ship mode", sorted(df["Ship Mode"].dropna().unique()), default=sorted(df["Ship Mode"].dropna().unique()))
threshold = st.sidebar.slider("Delay threshold (days)", 1, 1800, 30)

filtered = df[
    (df["Order Date"] >= start_date) &
    (df["Order Date"] <= end_date) &
    (df["Region"].isin(regions)) &
    (df["Ship Mode"].isin(modes))
].copy()

if states:
    filtered = filtered[filtered["State/Province"].isin(states)]

# ---------------- Data quality warning ----------------
ship_years = sorted(df["Ship Date"].dt.year.dropna().unique())
order_years = sorted(df["Order Date"].dt.year.dropna().unique())
suspicious_share = (df["Lead Time (Days)"] > threshold).mean()

with st.expander("⚠️ Data quality audit", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Missing values", f"{int(df.isna().sum().sum()):,}")
    c3.metric("Duplicate rows", f"{int(df.duplicated().sum()):,}")
    c4.metric(f"Lead times > {threshold}d", f"{suspicious_share:.1%}")

    st.write(
        f"Order dates span **{order_years[0]}–{order_years[-1]}**, while shipment dates span "
        f"**{ship_years[0]}–{ship_years[-1]}**. The supplied file therefore produces very large "
        f"positive lead times. This is a source-data issue that should be validated before using "
        f"the absolute lead-time values for operational decisions."
    )

# ---------------- KPI cards ----------------
st.header("Executive Overview")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Orders", f"{filtered['Order ID'].nunique():,}")
k2.metric("Shipments / Rows", f"{len(filtered):,}")
k3.metric("Sales", f"${filtered['Sales'].sum():,.2f}")
k4.metric("Gross Profit", f"${filtered['Gross Profit'].sum():,.2f}")
k5.metric("Avg Lead Time", f"{filtered['Lead Time (Days)'].mean():,.1f} d")

# ---------------- Route efficiency ----------------
st.header("1. Route Efficiency Overview")
route = (
    filtered.groupby(["Region", "State/Province"], dropna=False)
    .agg(
        Shipments=("Order ID", "count"),
        Avg_Lead_Time=("Lead Time (Days)", "mean"),
        Median_Lead_Time=("Lead Time (Days)", "median"),
        Lead_Time_SD=("Lead Time (Days)", "std"),
        Sales=("Sales", "sum"),
        Profit=("Gross Profit", "sum"),
    )
    .reset_index()
)
route["Delay_Frequency"] = (
    filtered.assign(Delayed=filtered["Lead Time (Days)"] > threshold)
    .groupby(["Region", "State/Province"])["Delayed"].mean()
    .values
)
route["Efficiency Score"] = 100 * route["Avg_Lead_Time"].min() / route["Avg_Lead_Time"]

col1, col2 = st.columns(2)
with col1:
    top = route.sort_values("Avg_Lead_Time").head(10)
    fig = px.bar(
        top.sort_values("Avg_Lead_Time", ascending=True),
        x="Avg_Lead_Time", y="State/Province", color="Region",
        orientation="h", title="Top 10 fastest customer-geography routes"
    )
    st.plotly_chart(fig, use_container_width=True)
with col2:
    bottom = route.sort_values("Avg_Lead_Time", ascending=False).head(10)
    fig = px.bar(
        bottom.sort_values("Avg_Lead_Time", ascending=True),
        x="Avg_Lead_Time", y="State/Province", color="Region",
        orientation="h", title="Bottom 10 slowest customer-geography routes"
    )
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    route.sort_values("Avg_Lead_Time").style.format({
        "Avg_Lead_Time": "{:.1f}", "Median_Lead_Time": "{:.1f}",
        "Lead_Time_SD": "{:.1f}", "Sales": "${:,.2f}",
        "Profit": "${:,.2f}", "Delay_Frequency": "{:.1%}",
        "Efficiency Score": "{:.1f}"
    }),
    use_container_width=True, hide_index=True
)

# ---------------- Geography ----------------
st.header("2. Geographic Bottleneck Analysis")
geo = (
    filtered.groupby("Region")
    .agg(
        Shipments=("Order ID", "count"),
        Avg_Lead_Time=("Lead Time (Days)", "mean"),
        Sales=("Sales", "sum"),
        Profit=("Gross Profit", "sum"),
    ).reset_index()
)
g1, g2 = st.columns(2)
with g1:
    fig = px.bar(geo.sort_values("Avg_Lead_Time"), x="Region", y="Avg_Lead_Time",
                 title="Average lead time by region", text_auto=".1f")
    st.plotly_chart(fig, use_container_width=True)
with g2:
    fig = px.scatter(
        geo, x="Shipments", y="Avg_Lead_Time", size="Sales",
        color="Region", hover_data=["Profit"],
        title="Volume vs. lead time"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Ship mode ----------------
st.header("3. Ship Mode Performance")
mode = (
    filtered.groupby("Ship Mode")
    .agg(
        Shipments=("Order ID", "count"),
        Avg_Lead_Time=("Lead Time (Days)", "mean"),
        Median_Lead_Time=("Lead Time (Days)", "median"),
        Sales=("Sales", "sum"),
        Profit=("Gross Profit", "sum"),
    ).reset_index()
)
fig = px.bar(mode, x="Ship Mode", y="Avg_Lead_Time", color="Ship Mode",
             title="Average lead time by shipping method", text_auto=".1f")
st.plotly_chart(fig, use_container_width=True)
st.dataframe(mode.style.format({
    "Avg_Lead_Time": "{:.1f}", "Median_Lead_Time": "{:.1f}",
    "Sales": "${:,.2f}", "Profit": "${:,.2f}"
}), use_container_width=True, hide_index=True)

# ---------------- Drill-down ----------------
st.header("4. Route Drill-Down")
selected_route = st.selectbox("Select a route", sorted(filtered["Route"].unique()))
detail = filtered[filtered["Route"] == selected_route].copy()

d1, d2, d3, d4 = st.columns(4)
d1.metric("Shipments", f"{len(detail):,}")
d2.metric("Avg Lead Time", f"{detail['Lead Time (Days)'].mean():,.1f} d")
d3.metric("Sales", f"${detail['Sales'].sum():,.2f}")
d4.metric("Profit", f"${detail['Gross Profit'].sum():,.2f}")

fig = px.histogram(detail, x="Lead Time (Days)", color="Ship Mode",
                   title=f"Lead-time distribution — {selected_route}")
st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    detail[[
        "Order ID", "Order Date", "Ship Date", "Ship Mode",
        "City", "State/Province", "Product Name", "Sales",
        "Units", "Gross Profit", "Lead Time (Days)"
    ]].sort_values("Order Date"),
    use_container_width=True, hide_index=True
)

# ---------------- Recommendations ----------------
st.header("5. Decision Support")
slowest_region = geo.loc[geo["Avg_Lead_Time"].idxmax(), "Region"] if len(geo) else "N/A"
fastest_mode = mode.loc[mode["Avg_Lead_Time"].idxmin(), "Ship Mode"] if len(mode) else "N/A"
st.markdown(f"""
- **Prioritize investigation:** {slowest_region} has the highest average lead time among the selected regions.
- **Benchmark shipping mode:** {fastest_mode} has the lowest reported average lead time in the selected data.
- **Route action:** Focus operational review on the bottom 10 routes by average lead time and high-volume routes with poor performance.
- **Data governance:** Validate the source shipment dates before using absolute lead-time values for service-level or cost decisions.
""")

st.caption("Note: The CSV does not contain a factory/origin-location field. Routes are therefore defined as Region → State/Province, not Factory → Customer.")
