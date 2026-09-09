"""
src/database/db_manager.py
Relational database management, SQLite schema execution, table loading,
view registration, and star-schema Power BI dataset exportation.
"""
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from sqlalchemy import create_engine

from src.utils.config import (
    DATABASE_PATH,
    POWERBI_DATA_DIR,
    PROCESSED_DATA_DIR,
    SQL_DIR,
    ensure_directories,
)
from src.utils.logging import get_logger

logger = get_logger("db_manager")


class DatabaseManager:
    """Manages SQLite database connections, DDL creation, and Power BI star-schema export."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DATABASE_PATH
        self.engine = create_engine(f"sqlite:///{self.db_path}")

    def execute_script(self, sql_script_path: Path) -> None:
        """Execute a multi-statement SQL script file."""
        if not sql_script_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_script_path}")

        with open(sql_script_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript(sql_content)
            conn.commit()

        logger.info(f"Executed SQL script: {sql_script_path.name}")

    def initialize_schema(self) -> None:
        """Create normalized relational tables."""
        schema_path = SQL_DIR / "schema.sql"
        self.execute_script(schema_path)

    def load_processed_tables(self) -> None:
        """Load processed CSV files into SQLite tables."""
        tables = ["customers", "products", "transactions", "reviews", "interactions"]
        for table in tables:
            csv_path = PROCESSED_DATA_DIR / f"{table}.csv"
            if not csv_path.exists():
                logger.warning(f"Missing processed table file: {csv_path}")
                continue

            df = pd.read_csv(csv_path)
            # Write to SQL (replace to ensure fresh clean load)
            df.to_sql(table, con=self.engine, if_exists="replace", index=False)
            logger.info(f"Loaded {len(df)} rows into SQL table '{table}'.")

        # Also load review_aspects if available
        aspects_path = PROCESSED_DATA_DIR / "review_aspects.csv"
        if aspects_path.exists():
            aspects_df = pd.read_csv(aspects_path)
            aspects_df.to_sql("review_aspects", con=self.engine, if_exists="replace", index=False)
            logger.info(f"Loaded {len(aspects_df)} rows into SQL table 'review_aspects'.")

    def create_powerbi_views(self) -> None:
        """Execute Power BI star-schema view definitions."""
        views_path = SQL_DIR / "powerbi_views.sql"
        self.execute_script(views_path)

    def export_powerbi_star_schema(self) -> None:
        """Export star-schema views to CSV in data/powerbi_export/."""
        ensure_directories()
        views = [
            "DimCustomer", "DimProduct", "DimCategory", "DimDate",
            "FactSales", "FactReviews", "FactInteractions"
        ]

        for view_name in views:
            query = f"SELECT * FROM {view_name};"
            df = pd.read_sql(query, con=self.engine)
            out_file = POWERBI_DATA_DIR / f"{view_name}.csv"
            df.to_csv(out_file, index=False)
            logger.info(f"Exported Power BI view {view_name}: {out_file} ({len(df)} rows)")

    def query(self, sql_query: str) -> pd.DataFrame:
        """Run analytical query and return DataFrame."""
        return pd.read_sql(sql_query, con=self.engine)


def setup_database_and_export():
    """Orchestrate end-to-end database setup, view creation, and Power BI dataset export."""
    ensure_directories()
    db = DatabaseManager()
    db.initialize_schema()
    db.load_processed_tables()
    db.create_powerbi_views()
    db.export_powerbi_star_schema()
    logger.info("Database and Power BI star-schema exports successfully completed.")


if __name__ == "__main__":
    setup_database_and_export()
