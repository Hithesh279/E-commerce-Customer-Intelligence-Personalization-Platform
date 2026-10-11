"""
src/analytics/templates.py
Pre-configured enterprise business dataset templates with realistic sample generators
and downloadable blank CSV schemas.
"""
from datetime import datetime, timedelta
import io
import random
from typing import Any, Dict, List
import pandas as pd


TEMPLATES_CONFIG: Dict[str, Dict[str, Any]] = {
    "product_reviews": {
        "id": "product_reviews",
        "name": "Customer Product Reviews & VoC",
        "icon": "💬",
        "category": "Voice of Customer & NLP",
        "description": "Customer feedback with star ratings, product titles, verified purchase status, and textual reviews for 11-aspect sentiment analysis.",
        "columns": [
            "review_id",
            "product_name",
            "rating",
            "review_text",
            "verified_purchase",
            "review_date",
        ],
        "sample_row": [
            "REV-1001",
            "Wireless Noise-Canceling Headphones",
            5,
            "The battery life is phenomenal and sound quality is crisp, but delivery was a bit slow.",
            "Yes",
            "2026-03-15",
        ],
    },
    "retail_transactions": {
        "id": "retail_transactions",
        "name": "Retail Sales & Order Transactions",
        "icon": "🛍️",
        "category": "Commerce & Sales",
        "description": "Multi-category e-commerce orders with transaction timestamps, customer IDs, product categories, quantities, amounts, and return flags.",
        "columns": [
            "order_id",
            "order_date",
            "customer_id",
            "product_name",
            "category",
            "quantity",
            "unit_price",
            "total_amount",
            "return_status",
        ],
        "sample_row": [
            "ORD-5001",
            "2026-02-10",
            "CUST-0842",
            "Ultra HD 4K Smart Monitor",
            "Electronics",
            1,
            389.99,
            389.99,
            "Completed",
        ],
    },
    "customer_rfm": {
        "id": "customer_rfm",
        "name": "Customer RFM & Loyalty Profiles",
        "icon": "👥",
        "category": "Customer Intelligence",
        "description": "Customer behavioral profiles with signup tenure, total order frequency, lifetime monetary spend, last purchase date, and loyalty tiers.",
        "columns": [
            "customer_id",
            "customer_name",
            "signup_date",
            "total_orders",
            "lifetime_spend",
            "last_order_date",
            "loyalty_tier",
        ],
        "sample_row": [
            "CUST-1029",
            "Sarah Jenkins",
            "2024-06-18",
            14,
            2450.80,
            "2026-03-01",
            "Platinum",
        ],
    },
    "inventory_health": {
        "id": "inventory_health",
        "name": "Product Catalog & Inventory Intelligence",
        "icon": "📦",
        "category": "Supply Chain & Catalog",
        "description": "SKU catalog intelligence with unit cost, selling price, current warehouse stock, 30-day velocity, margin rates, and return frequency.",
        "columns": [
            "sku",
            "product_name",
            "category",
            "cost_price",
            "selling_price",
            "stock_quantity",
            "units_sold_30d",
            "return_rate_pct",
        ],
        "sample_row": [
            "SKU-EL-094",
            "Mechanical Ergonomic Keyboard",
            "Electronics",
            45.00,
            119.99,
            85,
            142,
            3.5,
        ],
    },
    "support_tickets": {
        "id": "support_tickets",
        "name": "Customer Support Tickets & Feedback",
        "icon": "🎧",
        "category": "Customer Experience & Ops",
        "description": "Helpdesk resolution logs with channel intake, issue priority, agent resolution hours, customer CSAT score, and feedback comments.",
        "columns": [
            "ticket_id",
            "ticket_date",
            "customer_id",
            "channel",
            "priority",
            "resolution_time_hrs",
            "customer_feedback",
            "satisfaction_score",
        ],
        "sample_row": [
            "TCK-8821",
            "2026-01-22",
            "CUST-0419",
            "Live Chat",
            "High",
            3.5,
            "Support agent solved my refund issue swiftly. Excellent and polite service!",
            5,
        ],
    },
    "subscription_churn": {
        "id": "subscription_churn",
        "name": "Subscription & Churn Retention",
        "icon": "🔄",
        "category": "SaaS & Membership",
        "description": "Recurring subscription accounts with plan tiers, monthly recurring revenue (MRR), active tenure months, churn status, and exit feedback.",
        "columns": [
            "subscription_id",
            "customer_id",
            "plan_tier",
            "mrr_amount",
            "signup_date",
            "tenure_months",
            "churn_status",
            "exit_feedback",
        ],
        "sample_row": [
            "SUB-4011",
            "CUST-0914",
            "Professional",
            49.00,
            "2024-11-05",
            16,
            "Retained",
            "The platform saves our team hours of work every week. Great value.",
        ],
    },
}


def get_available_templates() -> Dict[str, Dict[str, Any]]:
    """Return dictionary of all available business templates."""
    return TEMPLATES_CONFIG


def generate_blank_template_csv(template_id: str) -> str:
    """Generate blank CSV text containing headers and one sample row for guidance."""
    if template_id not in TEMPLATES_CONFIG:
        raise ValueError(f"Unknown template ID: {template_id}")

    config = TEMPLATES_CONFIG[template_id]
    df = pd.DataFrame([config["sample_row"]], columns=config["columns"])
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()


def load_sample_template(template_id: str, n_records: int = 120) -> pd.DataFrame:
    """Generate rich, realistic synthetic data matching the chosen business template schema."""
    random.seed(42)
    now = datetime(2026, 3, 15)

    if template_id == "product_reviews":
        products = [
            ("Wireless Noise-Canceling Headphones", "Electronics"),
            ("Ergonomic Mesh Office Chair", "Furniture"),
            ("Stainless Steel Thermal Water Bottle", "Home & Kitchen"),
            ("Smart Fitness Tracker Band", "Electronics"),
            ("Organic Arabica Coffee Beans (1kg)", "Grocery"),
            ("Compact Dual-Port USB-C Fast Charger", "Electronics"),
            ("Breathable Running Shoes", "Apparel"),
            ("Mechanical RGB Gaming Keyboard", "Electronics"),
        ]
        sample_reviews = [
            ("The battery lasts all day and sound quality is phenomenal, very happy with the purchase!", 5),
            ("Super fast delivery and premium build quality. Worth every dollar.", 5),
            ("Decent product overall. Performance is good but the price is slightly steep.", 4),
            ("Camera and display are brilliant, however battery performance could be better.", 3),
            ("Customer service was unhelpful and delivery took over two weeks. Disappointed.", 1),
            ("Terrible durability. Broke down within four days of use. Avoid this.", 1),
            ("Sound is clear and comfortable to wear for hours. Great value for money.", 5),
            ("Packaging was completely crushed and items were scratched inside.", 2),
            ("Exceptional build quality and very intuitive usability. Highly recommended!", 5),
            ("Average quality. Does the job but nothing extraordinary for this price.", 3),
            ("Battery life is disappointing and drains rapidly even on standby.", 2),
            ("Outstanding performance and sleek design! Five stars.", 5),
        ]

        rows = []
        for i in range(n_records):
            prod, _ = random.choice(products)
            rev_text, base_rating = random.choice(sample_reviews)
            rating = max(1, min(5, base_rating + random.choice([-1, 0, 0, 1])))
            days_ago = random.randint(1, 180)
            rev_date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            verified = "Yes" if random.random() > 0.15 else "No"

            rows.append({
                "review_id": f"REV-{1000 + i}",
                "product_name": prod,
                "rating": rating,
                "review_text": rev_text,
                "verified_purchase": verified,
                "review_date": rev_date,
            })
        return pd.DataFrame(rows)

    elif template_id == "retail_transactions":
        catalog = [
            ("Ultra HD 4K Smart Monitor", "Electronics", 389.99),
            ("Noise-Canceling Wireless Earbuds", "Electronics", 129.50),
            ("Ergonomic Memory Foam Pillow", "Home & Kitchen", 45.00),
            ("Heavy-Duty Cast Iron Skillet", "Home & Kitchen", 59.90),
            ("Men's Lightweight Running Jacket", "Apparel", 79.99),
            ("Waterproof Trail Hiking Boots", "Apparel", 149.00),
            ("Organic Matcha Green Tea Powder", "Grocery", 28.50),
            ("Premium Bluetooth Soundbar", "Electronics", 199.99),
        ]
        rows = []
        for i in range(n_records):
            prod, cat, unit_price = random.choice(catalog)
            qty = random.choices([1, 2, 3, 4], weights=[0.65, 0.22, 0.09, 0.04])[0]
            total_amt = round(qty * unit_price, 2)
            days_ago = random.randint(1, 180)
            order_date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            cust_id = f"CUST-{random.randint(100, 160):04d}"
            is_returned = random.random() < 0.06
            status = "Returned" if is_returned else "Completed"

            rows.append({
                "order_id": f"ORD-{5000 + i}",
                "order_date": order_date,
                "customer_id": cust_id,
                "product_name": prod,
                "category": cat,
                "quantity": qty,
                "unit_price": unit_price,
                "total_amount": total_amt,
                "return_status": status,
            })
        return pd.DataFrame(rows)

    elif template_id == "customer_rfm":
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Casey", "Jamie"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson", "Taylor", "Clark"]
        tiers = ["Bronze", "Silver", "Gold", "Platinum"]

        rows = []
        for i in range(n_records):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            signup_days = random.randint(100, 800)
            signup_date = (now - timedelta(days=signup_days)).strftime("%Y-%m-%d")
            total_orders = max(1, int(random.expovariate(1 / 7)))
            avg_order = random.uniform(40.0, 220.0)
            lifetime_spend = round(total_orders * avg_order, 2)
            last_order_days = random.randint(1, min(signup_days, 180))
            last_order_date = (now - timedelta(days=last_order_days)).strftime("%Y-%m-%d")

            if lifetime_spend > 2500 or total_orders > 15:
                tier = "Platinum"
            elif lifetime_spend > 1000 or total_orders > 8:
                tier = "Gold"
            elif lifetime_spend > 350 or total_orders > 3:
                tier = "Silver"
            else:
                tier = "Bronze"

            rows.append({
                "customer_id": f"CUST-{1000 + i}",
                "customer_name": name,
                "signup_date": signup_date,
                "total_orders": total_orders,
                "lifetime_spend": lifetime_spend,
                "last_order_date": last_order_date,
                "loyalty_tier": tier,
            })
        return pd.DataFrame(rows)

    elif template_id == "inventory_health":
        sku_items = [
            ("SKU-EL-101", "Mechanical Ergonomic Keyboard", "Electronics", 45.00, 119.99),
            ("SKU-EL-102", "Dual-Port USB-C Fast Charger", "Electronics", 12.00, 34.99),
            ("SKU-EL-103", "Noise-Canceling Wireless Headphones", "Electronics", 68.00, 179.99),
            ("SKU-HK-201", "Stainless Steel Thermal Tumbler", "Home & Kitchen", 8.50, 29.50),
            ("SKU-HK-202", "Cast Iron Skillet Pan (10-inch)", "Home & Kitchen", 22.00, 54.99),
            ("SKU-AP-301", "Breathable Waterproof Jacket", "Apparel", 35.00, 89.99),
            ("SKU-AP-302", "High-Elastic Athletic Leggings", "Apparel", 16.00, 48.00),
            ("SKU-GR-401", "Organic Arabica Coffee (1kg)", "Grocery", 11.50, 26.00),
            ("SKU-FN-501", "Adjustable Lumbar Support Chair", "Furniture", 110.00, 289.00),
            ("SKU-FN-502", "Electric Standing Desk Frame", "Furniture", 160.00, 399.00),
        ]
        rows = []
        for i in range(max(len(sku_items), min(n_records, 60))):
            base_item = sku_items[i % len(sku_items)]
            sku = f"{base_item[0]}-{i // len(sku_items) + 1}" if i >= len(sku_items) else base_item[0]
            stock = random.randint(5, 250)
            velocity = random.randint(15, 180)
            ret_rate = round(random.uniform(1.2, 9.8), 1)

            rows.append({
                "sku": sku,
                "product_name": base_item[1],
                "category": base_item[2],
                "cost_price": base_item[3],
                "selling_price": base_item[4],
                "stock_quantity": stock,
                "units_sold_30d": velocity,
                "return_rate_pct": ret_rate,
            })
        return pd.DataFrame(rows)

    elif template_id == "support_tickets":
        channels = ["Live Chat", "Email", "Phone", "Portal"]
        priorities = ["Low", "Medium", "High", "Critical"]
        feedback_pool = [
            ("The support agent solved my refund swiftly. Great service!", 5, 1.5),
            ("Quick response and helpful explanation for the warranty issue.", 5, 2.0),
            ("Waited on hold for 40 minutes. Problem eventually solved.", 3, 6.2),
            ("Issue was resolved within SLA, but agent was quite abrupt.", 3, 4.0),
            ("Terrible support. My replacement was never shipped.", 1, 18.5),
            ("Excellent assistance with my account authentication reset.", 5, 0.8),
            ("Agent did not understand the billing problem and had to escalate.", 2, 12.0),
            ("Polite and friendly representative. Resolved on first call.", 5, 1.2),
        ]
        rows = []
        for i in range(n_records):
            fb, score, hrs = random.choice(feedback_pool)
            days_ago = random.randint(1, 90)
            tck_date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            actual_hrs = round(max(0.5, hrs + random.uniform(-0.8, 1.5)), 1)
            actual_score = max(1, min(5, score + random.choice([0, 0, -1, 1])))

            rows.append({
                "ticket_id": f"TCK-{8000 + i}",
                "ticket_date": tck_date,
                "customer_id": f"CUST-{random.randint(100, 160):04d}",
                "channel": random.choice(channels),
                "priority": random.choice(priorities),
                "resolution_time_hrs": actual_hrs,
                "customer_feedback": fb,
                "satisfaction_score": actual_score,
            })
        return pd.DataFrame(rows)

    elif template_id == "subscription_churn":
        plans = [("Starter", 19.00), ("Professional", 49.00), ("Enterprise", 149.00)]
        exit_comments = [
            ("Platform saves our team hours of work every week. Great value.", "Retained"),
            ("Very satisfied with uptime and API response times.", "Retained"),
            ("Love the custom analytics dashboards and customer tracking.", "Retained"),
            ("Switched to an all-in-one suite. Missing native CRM connector.", "Churned"),
            ("Monthly pricing is too high for our current startup stage.", "Churned"),
            ("Great product but company downsized our data science team.", "Churned"),
            ("Support response times have been exceptional.", "Retained"),
            ("Platform is intuitive and easy to integrate with BigQuery.", "Retained"),
        ]
        rows = []
        for i in range(n_records):
            plan_name, fee = random.choice(plans)
            comment, churn_stat = random.choice(exit_comments)
            tenure = random.randint(1, 36)
            signup_days = tenure * 30 + random.randint(1, 25)
            signup_date = (now - timedelta(days=signup_days)).strftime("%Y-%m-%d")

            rows.append({
                "subscription_id": f"SUB-{4000 + i}",
                "customer_id": f"CUST-{random.randint(100, 200):04d}",
                "plan_tier": plan_name,
                "mrr_amount": fee,
                "signup_date": signup_date,
                "tenure_months": tenure,
                "churn_status": churn_stat,
                "exit_feedback": comment,
            })
        return pd.DataFrame(rows)

    else:
        raise ValueError(f"Unknown template ID: {template_id}")
