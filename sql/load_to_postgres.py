"""
sql/load_to_postgres.py
Script to load processed e-commerce datasets into any local or remote PostgreSQL instance.
Requires psycopg2 and DATABASE_URL environment variable (or command line argument).
"""
import os
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

# Resolve paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
POSTGRES_SCHEMA = PROJECT_ROOT / "sql" / "postgres_schema.sql"


def load_postgres(db_url: str = None):
    """Load tables into PostgreSQL."""
    target_url = db_url or os.getenv("DATABASE_URL")
    if not target_url or not target_url.startswith("postgresql"):
        print("Please set DATABASE_URL (e.g. postgresql://postgres:password@localhost:5432/ecommerce_db)")
        sys.exit(1)

    print(f"Connecting to PostgreSQL: {target_url.split('@')[-1]}")
    engine = create_engine(target_url)

    # Execute DDL
    with open(POSTGRES_SCHEMA, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with engine.connect() as conn:
        conn.execute(schema_sql)
        print("PostgreSQL schema created successfully.")

    # Load tables
    tables = ["customers", "products", "transactions", "reviews", "interactions", "review_aspects"]
    for t in tables:
        csv_path = PROCESSED_DIR / f"{t}.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            df.to_sql(t, con=engine, if_exists="append", index=False)
            print(f"Loaded {len(df)} rows into {t}")

    print("PostgreSQL database setup complete!")


if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else None
    load_postgres(url_arg)
