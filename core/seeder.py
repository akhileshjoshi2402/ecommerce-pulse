from datetime import datetime, timedelta
import numpy as np
from psycopg2.extras import execute_values
from db.connection import get_db_connection


def generate_products() -> list[tuple]:
    catalog_templates = {
        'Electronics': {
            'items': ['Wireless Headphones', 'Mechanical Keyboard', 'Gaming Mouse', '4K Monitor', 'USB-C Hub'],
            'price_range': (40.0, 500.0)
        },
        'Clothing': {
            'items': ['Cotton T-Shirt', 'Denim Jeans', 'Hoodie', 'Running Shoes', 'Winter Jacket'],
            'price_range': (20.0, 150.0)
        },
        'Home': {
            'items': ['Desk Lamp', 'Air Purifier', 'Coffee Maker', 'Ergonomic Chair', 'Blender'],
            'price_range': (35.0, 300.0)
        },
        'Books': {
            'items': ['Python Programming Guide', 'Data Science Handbook', 'System Design Manual', 'SQL Mastery', 'Deep Learning Concepts'],
            'price_range': (15.0, 60.0)
        }
    }

    products = []
    for category, meta in catalog_templates.items():
        for item_name in meta['items']:
            low, high = meta['price_range']
            price = round(float(np.random.uniform(low, high)), 2)
            products.append((item_name, category, price))
            
    return products


def generate_customers(n: int = 50) -> list[tuple]:
    first_names = ['Aarav', 'Ananya', 'Rohan', 'Pooja', 'Vikram', 'Neha', 'Aditya', 'Sneha', 'Rahul', 'Kavita']
    last_names = ['Sharma', 'Verma', 'Patel', 'Joshi', 'Mehta', 'Nair', 'Rao', 'Iyer', 'Gupta', 'Singh']
    domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'proton.me']

    customers = []
    for i in range(1, n + 1):
        first = str(np.random.choice(first_names))
        last = str(np.random.choice(last_names))
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{i}@{np.random.choice(domains)}"
        days_ago = int(np.random.randint(30, 365))
        signup_date = datetime.now() - timedelta(days=days_ago)
        customers.append((name, email, signup_date))

    return customers


def seed_data(num_orders: int = 200) -> None:
    conn = get_db_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                # 1. Insert Products
                product_data = generate_products()
                query_product = """
                    INSERT INTO products (product_name, category, unit_price)
                    VALUES %s
                    RETURNING product_id, unit_price;
                """
                products_db = execute_values(cur, query_product, product_data, fetch=True)
                print(f"Inserted {len(products_db)} products.")

                # 2. Insert Customers
                customer_data = generate_customers(50)
                query_customer = """
                    INSERT INTO customers (customer_name, email, signup_date)
                    VALUES %s
                    RETURNING customer_id, signup_date;
                """
                customers_db = execute_values(cur, query_customer, customer_data, fetch=True)
                print(f"Inserted {len(customers_db)} customers.")

                # 3. Insert Orders
                order_records = []
                for _ in range(num_orders):
                    idx = np.random.randint(len(customers_db))
                    c_id, signup_date = customers_db[idx]
                    
                    seconds_since_signup = int((datetime.now(signup_date.tzinfo) - signup_date).total_seconds())
                    order_offset_seconds = int(np.random.randint(0, max(1, seconds_since_signup)))
                    order_date = signup_date + timedelta(seconds=order_offset_seconds)
                    
                    status = str(np.random.choice(["Completed", "Cancelled", "Returned"], p=[0.8, 0.1, 0.1]))
                    order_records.append((c_id, order_date, status))

                query_orders = """
                    INSERT INTO orders (customer_id, order_date, status)
                    VALUES %s
                    RETURNING order_id;
                """
                orders_db = execute_values(cur, query_orders, order_records, fetch=True)
                print(f"Inserted {len(orders_db)} orders.")

                # 4. Insert Order Items
                order_item_records = []
                for (o_id,) in orders_db:
                    num_items = int(np.random.randint(1, 5))
                    chosen_indices = np.random.choice(len(products_db), size=num_items, replace=False)

                    for p_idx in chosen_indices:
                        p_id, unit_price = products_db[p_idx]
                        quantity = int(np.random.randint(1, 4))
                        order_item_records.append((o_id, p_id, quantity, unit_price))

                query_order_items = """
                    INSERT INTO order_items (order_id, product_id, quantity, price_per_unit)
                    VALUES %s;
                """
                execute_values(cur, query_order_items, order_item_records)
                print(f"Inserted {len(order_item_records)} order items.")

        print("Database seeded successfully.")

    finally:
        conn.close()


if __name__ == "__main__":
    seed_data()