import os
import pandas as pd
import psycopg2
from db.connection import get_db_connection


def init_db(schema_path: str = "db/schema.sql") -> None:
    """Reads schema.sql and creates relational tables in Supabase."""
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
        print("Tables initialized successfully.")
    except psycopg2.Error as e:
        print(f"Failed to execute schema migration: {e}")
        raise
    finally:
        conn.close()


def fetch_dataframe(query: str, params: tuple = None) -> pd.DataFrame:
    """Executes a SELECT query and returns the results as a Pandas DataFrame."""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except psycopg2.Error as e:
        print(f"Database query error: {e}")
        raise
    finally:
        conn.close()


def get_master_transaction_data() -> pd.DataFrame:
    """
    Retrieves a denormalized transaction dataset joining orders,
    customers, order_items, and products.
    """
    query = """
        SELECT 
            o.order_id,
            o.order_date,
            o.status,
            c.customer_id,
            c.customer_name,
            c.email,
            c.signup_date,
            p.product_id,
            p.product_name,
            p.category,
            oi.quantity,
            oi.price_per_unit,
            (oi.quantity * oi.price_per_unit) AS line_total
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        ORDER BY o.order_date DESC;
    """
    return fetch_dataframe(query)


def get_customer_rfm_raw() -> pd.DataFrame:
    """
    Retrieves aggregated customer-level purchase statistics
    for completed orders to power RFM segmentation.
    """
    query = """
        SELECT 
            c.customer_id,
            c.customer_name,
            c.email,
            c.signup_date,
            MAX(o.order_date) AS last_order_date,
            COUNT(DISTINCT o.order_id) AS total_orders,
            COALESCE(SUM(oi.quantity * oi.price_per_unit), 0) AS total_spend
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'Completed'
        GROUP BY c.customer_id, c.customer_name, c.email, c.signup_date
        ORDER BY total_spend DESC;
    """
    return fetch_dataframe(query)


if __name__ == "__main__":
    print("Testing master transaction query...")
    df_master = get_master_transaction_data()
    print(f"Master Records Retrieved: {len(df_master)}")
    print(df_master.head(2))

    print("\nTesting RFM aggregate query...")
    df_rfm = get_customer_rfm_raw()
    print(f"Customer Summaries Retrieved: {len(df_rfm)}")
    print(df_rfm.head(2))