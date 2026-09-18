import os
import sys
from pathlib import Path

# Add project root directory to sys.path so 'db' and 'core' modules resolve cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd

from db.repository import get_master_transaction_data, get_customer_rfm_raw
from core.metrics import calculate_kpis, calculate_rfm_segments, generate_cohort_matrix
from core.visualizer import plot_revenue_over_time, plot_rfm_distribution, plot_cohort_heatmap

# Page configuration
st.set_page_config(
    page_title="E-Commerce Pulse Analytics",
    page_icon="📈",
    layout="wide"
)

# Header
st.title("📈 E-Commerce Pulse Analytics Dashboard")
st.caption("Real-time transactional business metrics, customer cohorts, and RFM segmentation.")
st.divider()

# Cached data loaders
@st.cache_data(ttl=300)
def load_transaction_data() -> pd.DataFrame:
    return get_master_transaction_data()

@st.cache_data(ttl=300)
def load_rfm_data() -> pd.DataFrame:
    return get_customer_rfm_raw()

with st.spinner("Connecting to Supabase and fetching transactional data..."):
    df_master = load_transaction_data()
    df_rfm_raw = load_rfm_data()

if df_master.empty:
    st.warning("No transactional data found. Please run the seeder first.")
    st.stop()

# Sidebar: Filters
st.sidebar.header("Dashboard Filters")

all_categories = sorted(df_master["category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Filter by Product Category:",
    options=all_categories,
    default=all_categories
)

# Ensure timezone-naive comparison for date slider
df_master["order_date"] = pd.to_datetime(df_master["order_date"]).dt.tz_localize(None)
min_date = df_master["order_date"].min().date()
max_date = df_master["order_date"].max().date()

selected_date_range = st.sidebar.date_input(
    "Select Date Range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply filters
filtered_master = df_master[df_master["category"].isin(selected_categories)]

if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_d, end_d = selected_date_range
    filtered_master = filtered_master[
        (filtered_master["order_date"].dt.date >= start_d) &
        (filtered_master["order_date"].dt.date <= end_d)
    ]

# Section 1: KPI Cards
kpis = calculate_kpis(filtered_master)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Revenue", f"${kpis['total_revenue']:,.2f}")
col2.metric("Total Orders", f"{kpis['total_orders']:,}")
col3.metric("Completed Orders", f"{kpis['completed_orders']:,}")
col4.metric("Average Order Value", f"${kpis['average_order_value']:,.2f}")
col5.metric("Return Rate", f"{kpis['return_rate']:.1f}%")

st.divider()

# Section 2: Visual Analytics
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Monthly Revenue Trajectory")
    if not filtered_master.empty:
        fig_rev = plot_revenue_over_time(filtered_master)
        st.pyplot(fig_rev, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with col_right:
    st.subheader("Customer Segment Distribution")
    df_rfm = calculate_rfm_segments(df_rfm_raw)
    fig_rfm = plot_rfm_distribution(df_rfm)
    st.pyplot(fig_rfm, use_container_width=True)

st.divider()

# Section 3: Cohort Retention Matrix
st.subheader("Monthly Customer Retention Matrix (%)")
retention_matrix = generate_cohort_matrix(df_master)
if not retention_matrix.empty:
    fig_cohort = plot_cohort_heatmap(retention_matrix)
    st.pyplot(fig_cohort, use_container_width=True)
else:
    st.info("Retention matrix could not be computed.")

# Section 4: Data Explorer
with st.expander("🔍 View Raw Master Transactions"):
    st.dataframe(filtered_master, use_container_width=True)