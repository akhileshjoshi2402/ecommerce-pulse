# 📈 E-Commerce Pulse Analytics

A full-stack transactional analytics engine and interactive dashboard built with **Python**, **PostgreSQL (Supabase)**, and **Streamlit**.

The platform ingests multi-table relational e-commerce transactions, computes core business KPIs, segments customers via **RFM (Recency, Frequency, Monetary)** quartiles, and models retention patterns using **triangular cohort matrices**.

---

## 🏗️ Architecture & Stack

- **Frontend / Presentation:** Streamlit (Dynamic interactive filters, KPI metric scorecards, Matplotlib/Seaborn visualizations)
- **Analytics & Feature Engineering:** Pure vectorized NumPy & Pandas (`core/metrics.py`)
- **Database & Storage:** PostgreSQL via Supabase (`db/schema.sql`, `db/repository.py`)
- **Visualizations:** Object-Oriented Matplotlib & Seaborn (`core/visualizer.py`)
- **Dependency Management:** `uv` (Fast Python package resolver)
- **Testing:** `pytest` (Unit tests verifying analytical computations)

---

## 🚀 Key Features

1. **Transactional Metrics Engine:** Real-time computation of Total Revenue, Completed Orders, Average Order Value (AOV), Return Rate, and Cancellation Rate.
2. **RFM Customer Segmentation:** Vectorized quartile binning (`pd.qcut`) assigning customers into tiers: *Champions*, *Loyal Customers*, and *At Risk*.
3. **Monthly Retention Cohort Heatmap:** Tracks initial sign-up retention percentages decay over subsequent purchase months.
4. **Interactive Exploratory UI:** Filter transaction timelines and product categories dynamically.

---

## 🛠️ Getting Started

### 1. Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) installed
- Supabase PostgreSQL instance

### 2. Setup Environment
Clone the repository and install dependencies:
```bash
git clone [https://github.com/akhileshjoshi2402/ecommerce-pulse.git](https://github.com/akhileshjoshi2402/ecommerce-pulse.git)
cd ecommerce-pulse
uv sync