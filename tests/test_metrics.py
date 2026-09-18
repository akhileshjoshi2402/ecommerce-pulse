import pandas as pd
import numpy as np
import pytest
from core.metrics import calculate_kpis, calculate_rfm_segments, generate_cohort_matrix

@pytest.fixture
def mock_transaction_data():
    """Provides a synthetic transactions dataset with known results."""
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4],
        "order_date": pd.to_datetime([
            "2026-01-10", "2026-01-15", "2026-02-10", "2026-02-12"
        ]),
        "status": ["Completed", "Completed", "Cancelled", "Returned"],
        "customer_id": [101, 102, 101, 103],
        "customer_name": ["Alice", "Bob", "Alice", "Charlie"],
        "category": ["Electronics", "Books", "Electronics", "Clothing"],
        "quantity": [2, 1, 1, 3],
        "price_per_unit": [100.0, 50.0, 100.0, 30.0],
        "line_total": [200.0, 50.0, 100.0, 90.0]
    })

@pytest.fixture
def mock_rfm_raw_data():
    """Provides synthetic customer purchase summaries."""
    return pd.DataFrame({
        "customer_id": [1, 2, 3, 4],
        "customer_name": ["User A", "User B", "User C", "User D"],
        "email": ["a@test.com", "b@test.com", "c@test.com", "d@test.com"],
        "signup_date": pd.to_datetime(["2025-01-01", "2025-02-01", "2025-03-01", "2025-04-01"]),
        "last_order_date": pd.to_datetime(["2026-09-01", "2026-08-15", "2026-05-01", "2026-01-01"]),
        "total_orders": [12, 8, 3, 1],
        "total_spend": [5000.0, 3000.0, 800.0, 150.0]
    })

# -----------------------------------------------------------------------------
# KPI Verification Tests
# -----------------------------------------------------------------------------
def test_calculate_kpis_math(mock_transaction_data):
    kpis = calculate_kpis(mock_transaction_data)
    
    # 2 completed orders ($200 + $50) = $250 total
    assert kpis["total_revenue"] == 250.0
    assert kpis["total_orders"] == 4
    assert kpis["completed_orders"] == 2
    # 250 / 2 = 125.0 AOV
    assert kpis["average_order_value"] == 125.0
    # 1 cancelled out of 4 = 25%
    assert kpis["cancellation_rate"] == 25.0
    # 1 returned out of 4 = 25%
    assert kpis["return_rate"] == 25.0

def test_calculate_kpis_empty():
    empty_df = pd.DataFrame(columns=["order_id", "status", "line_total"])
    kpis = calculate_kpis(empty_df)
    assert kpis["total_revenue"] == 0.0
    assert kpis["total_orders"] == 0
    assert kpis["average_order_value"] == 0.0

# -----------------------------------------------------------------------------
# RFM Segmentation Verification Tests
# -----------------------------------------------------------------------------
def test_calculate_rfm_segment_ranks(mock_rfm_raw_data):
    df_rfm = calculate_rfm_segments(mock_rfm_raw_data)
    
    # Check that required columns are created
    assert "r_score" in df_rfm.columns
    assert "f_score" in df_rfm.columns
    assert "m_score" in df_rfm.columns
    assert "rfm_segment" in df_rfm.columns
    
    # User A has lowest recency days, highest orders, highest spend -> Top tier
    user_a = df_rfm[df_rfm["customer_id"] == 1].iloc[0]
    assert user_a["r_score"] == 4
    assert user_a["f_score"] == 4
    assert user_a["m_score"] == 4
    assert user_a["rfm_segment"] == "Champions"

# -----------------------------------------------------------------------------
# Cohort Retention Verification Tests
# -----------------------------------------------------------------------------
def test_generate_cohort_matrix_structure(mock_transaction_data):
    matrix = generate_cohort_matrix(mock_transaction_data)
    
    assert not matrix.empty
    # Initial month (Index 0) retention must always equal 100%
    assert 0 in matrix.columns
    assert (matrix[0] == 100.0).all()