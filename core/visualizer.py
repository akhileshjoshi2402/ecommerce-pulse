import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Consistent aesthetic styling
sns.set_theme(style="whitegrid", palette="muted")


def plot_revenue_over_time(df: pd.DataFrame) -> plt.Figure:
    """Generates a monthly revenue line chart with marked trend points."""
    completed = df[df["status"] == "Completed"].copy()
    completed["order_date"] = pd.to_datetime(completed["order_date"])

    monthly_rev = (
        completed.resample("ME", on="order_date")["line_total"]
        .sum()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 4.5))
    sns.lineplot(
        data=monthly_rev,
        x="order_date",
        y="line_total",
        marker="o",
        color="#2b5c8f",
        linewidth=2.5,
        ax=ax,
    )

    ax.set_title("Monthly Revenue Trend", fontsize=14, pad=12, weight="bold")
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Revenue ($)", fontsize=11)
    fig.autofmt_xdate()
    plt.tight_layout()
    return fig


def plot_rfm_distribution(df_rfm: pd.DataFrame) -> plt.Figure:
    """Generates a horizontal bar count of customer tiers."""
    fig, ax = plt.subplots(figsize=(8, 4))
    order = ["Champions", "Loyal Customers", "At Risk", "Inactive / New"]

    sns.countplot(
        data=df_rfm,
        y="rfm_segment",
        order=[s for s in order if s in df_rfm["rfm_segment"].unique()],
        palette="viridis",
        hue="rfm_segment",
        legend=False,
        ax=ax,
    )

    ax.set_title("Customer RFM Segments", fontsize=14, pad=12, weight="bold")
    ax.set_xlabel("Customer Count", fontsize=11)
    ax.set_ylabel("")
    plt.tight_layout()
    return fig


def plot_cohort_heatmap(retention_matrix: pd.DataFrame) -> plt.Figure:
    """Plots the triangular monthly customer retention heatmap."""
    fig, ax = plt.subplots(
        figsize=(11, max(4, len(retention_matrix) * 0.45 + 1.5))
    )

    y_labels = [str(period) for period in retention_matrix.index]

    sns.heatmap(
        retention_matrix,
        annot=True,
        fmt=".0f",
        cmap="Blues",
        cbar_kws={"label": "Retention (%)"},
        yticklabels=y_labels,
        linewidths=0.5,
        ax=ax,
    )

    ax.set_title(
        "Monthly Cohort Customer Retention (%)",
        fontsize=14,
        pad=12,
        weight="bold",
    )
    ax.set_xlabel("Cohort Month Index", fontsize=11)
    ax.set_ylabel("Cohort Sign-up Month", fontsize=11)
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    from core.metrics import calculate_rfm_segments, generate_cohort_matrix
    from db.repository import get_customer_rfm_raw, get_master_transaction_data

    print("Generating and testing visualization outputs...")
    df_master = get_master_transaction_data()
    df_rfm = calculate_rfm_segments(get_customer_rfm_raw())
    retention = generate_cohort_matrix(df_master)

    fig1 = plot_revenue_over_time(df_master)
    fig1.savefig("revenue_trend.png")

    fig2 = plot_rfm_distribution(df_rfm)
    fig2.savefig("rfm_distribution.png")

    fig3 = plot_cohort_heatmap(retention)
    fig3.savefig("cohort_heatmap.png")

    print("Charts generated: revenue_trend.png, rfm_distribution.png, cohort_heatmap.png")