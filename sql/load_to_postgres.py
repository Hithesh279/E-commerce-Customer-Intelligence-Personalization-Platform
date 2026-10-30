"""
sql/load_to_postgres.py
Loads the processed CSV datasets into a PostgreSQL database.

Usage:
    DATABASE_URL=postgresql://user:pass@localhost:5432/ecommerce_db python sql/load_to_postgres.py
    python sql/load_to_postgres.py postgresql://user:pass@localhost:5432/ecommerce_db

Requires: pip install psycopg2-binary
The script drops and recreates all tables, so it is safe to re-run.
"""
import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
POSTGRES_SCHEMA = PROJECT_ROOT / "sql" / "postgres_schema.sql"
TABLES = ["customers", "products", "transactions", "reviews", "interactions", "review_aspects"]


def load_postgres(db_url: str = None) -> None:
    """Create the PostgreSQL schema and load all processed tables."""
    target_url = db_url or os.getenv("DATABASE_URL")
    if not target_url or not target_url.startswith("postgresql"):
        print("Please set DATABASE_URL (e.g. postgresql://postgres:password@localhost:5432/ecommerce_db)")
        sys.exit(1)

    print(f"Connecting to PostgreSQL: {target_url.split('@')[-1]}")
    engine = create_engine(target_url)

    schema_sql = POSTGRES_SCHEMA.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(schema_sql))
    print("PostgreSQL schema created successfully.")

    for table in TABLES:
        csv_path = PROCESSED_DIR / f"{table}.csv"
        if not csv_path.exists():
            print(f"Skipping {table}: {csv_path} not found")
            continue
        df = pd.read_csv(csv_path)
        df.to_sql(table, con=engine, if_exists="append", index=False, method="multi", chunksize=1000)
        print(f"Loaded {len(df)} rows into {table}")

    print("PostgreSQL database setup complete!")


if __name__ == "__main__":
    load_postgres(sys.argv[1] if len(sys.argv) > 1 else None)
