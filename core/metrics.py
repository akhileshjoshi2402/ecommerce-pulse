from datetime import datetime
import numpy as np
import pandas as pd
from db.repository import get_customer_rfm_raw, get_master_transaction_data


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Computes high-level business metrics from master transactional data."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_orders": 0,
            "completed_orders": 0,
            "average_order_value": 0.0,
            "cancellation_rate": 0.0,
            "return_rate": 0.0,
        }

    total_orders = df["order_id"].nunique()
    completed_df = df[df["status"] == "Completed"]
    completed_orders = completed_df["order_id"].nunique()

    # Total revenue from line totals of completed transactions
    total_revenue = round(float(completed_df["line_total"].sum()), 2)

    # Average Order Value (AOV)
    aov = (
        round(total_revenue / completed_orders, 2)
        if completed_orders > 0
        else 0.0
    )

    # Resolution rates across distinct orders
    cancelled_orders = df[df["status"] == "Cancelled"]["order_id"].nunique()
    returned_orders = df[df["status"] == "Returned"]["order_id"].nunique()

    cancellation_rate = (
        round((cancelled_orders / total_orders) * 100, 2)
        if total_orders > 0
        else 0.0
    )
    return_rate = (
        round((returned_orders / total_orders) * 100, 2)
        if total_orders > 0
        else 0.0
    )

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "average_order_value": aov,
        "cancellation_rate": cancellation_rate,
        "return_rate": return_rate,
    }


def calculate_rfm_segments(df_rfm: pd.DataFrame) -> pd.DataFrame:
    """Computes Recency, Frequency, Monetary (RFM) quartiles and assigns customer tiers."""
    if df_rfm.empty:
        return df_rfm

    df = df_rfm.copy()

    # Convert last_order_date to datetime if necessary
    df["last_order_date"] = pd.to_datetime(df["last_order_date"])

    # Recency: elapsed days from global maximum transaction date
    ref_date = df["last_order_date"].max()
    df["recency_days"] = (ref_date - df["last_order_date"]).dt.days

    # Quartile scoring: lower recency_days gets higher score (4)
    # Using rank(method='first') avoids issues with duplicate bin edges in small sample sets
    df["r_score"] = pd.qcut(
        df["recency_days"].rank(method="first"),
        q=4,
        labels=[4, 3, 2, 1],
    ).astype(int)

    df["f_score"] = pd.qcut(
        df["total_orders"].rank(method="first"),
        q=4,
        labels=[1, 2, 3, 4],
    ).astype(int)

    df["m_score"] = pd.qcut(
        df["total_spend"].rank(method="first"),
        q=4,
        labels=[1, 2, 3, 4],
    ).astype(int)

    df["rfm_score"] = df["r_score"] + df["f_score"] + df["m_score"]

    # Segment mapping using vectorized conditional rules
    conditions = [
        (df["r_score"] >= 3) & (df["f_score"] >= 3) & (df["m_score"] >= 3),
        (df["f_score"] >= 3),
        (df["r_score"] <= 2) & (df["f_score"] >= 2),
    ]
    choices = ["Champions", "Loyal Customers", "At Risk"]

    df["rfm_segment"] = np.select(conditions, choices, default="Inactive / New")
    return df


def generate_cohort_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Generates a monthly customer retention percentage matrix."""
    completed_df = df[df["status"] == "Completed"].copy()
    if completed_df.empty:
        return pd.DataFrame()

    completed_df["order_date"] = pd.to_datetime(
        completed_df["order_date"]
    ).dt.tz_localize(None)

    # Monthly periods for orders and initial customer cohorts
    completed_df["order_month"] = completed_df["order_date"].dt.to_period("M")
    completed_df["cohort_month"] = completed_df.groupby("customer_id")[
        "order_month"
    ].transform("min")

    # Offset in months between the order month and cohort month
    completed_df["cohort_index"] = (
        completed_df["order_month"].dt.year
        - completed_df["cohort_month"].dt.year
    ) * 12 + (
        completed_df["order_month"].dt.month
        - completed_df["cohort_month"].dt.month
    )

    # Pivot customer count per cohort over cohort index
    cohort_data = (
        completed_df.groupby(["cohort_month", "cohort_index"])["customer_id"]
        .nunique()
        .reset_index()
    )

    cohort_pivot = cohort_data.pivot_table(
        index="cohort_month",
        columns="cohort_index",
        values="customer_id",
    )

    # Divide by the initial cohort size (month 0) to get retention rate
    cohort_size = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0).round(4) * 100

    return retention_matrix


if __name__ == "__main__":
    print("Fetching data from repository...")
    df_master = get_master_transaction_data()
    df_rfm = get_customer_rfm_raw()

    print("\n--- KPI Breakdown ---")
    kpi_results = calculate_kpis(df_master)
    for k, v in kpi_results.items():
        print(f"{k}: {v}")

    print("\n--- RFM Segments (Top 5) ---")
    rfm_df = calculate_rfm_segments(df_rfm)
    print(
        rfm_df[
            [
                "customer_name",
                "recency_days",
                "total_orders",
                "total_spend",
                "rfm_segment",
            ]
        ].head()
    )

    print("\n--- Cohort Retention Matrix (%) ---")
    retention = generate_cohort_matrix(df_master)
    print(retention.head())