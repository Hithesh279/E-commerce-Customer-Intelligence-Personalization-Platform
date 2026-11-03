"""
src/database/db_manager.py
SQLite database management: rebuilds the schema from sql/schema.sql, loads the processed CSV tables,
creates the Power BI views and exports the star schema to CSV and Excel.

The SQLite file is always rebuilt from the canonical DDL, so table constraints and indexes are kept.
DATABASE_URL is not used here; it is read only by sql/load_to_postgres.py.
"""
import sqlite3
import zipfile
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Iterator, Optional

import pandas as pd

from src.utils.config import DATABASE_PATH, POWERBI_DATA_DIR, PROJECT_ROOT, PROCESSED_DATA_DIR, SQL_DIR, ensure_directories
from src.utils.logging import get_logger

logger = get_logger("db_manager")

# Load order matches foreign-key dependencies (parents first).
CORE_TABLES = ["customers", "products", "transactions", "reviews", "interactions", "review_aspects"]
POWERBI_VIEWS = ["DimCustomer", "DimProduct", "DimCategory", "DimDate", "FactSales", "FactReviews", "FactInteractions"]


class DatabaseManager:
    """Manages SQLite connections, DDL creation, table loading and Power BI star-schema export."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or DATABASE_PATH)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """Open a SQLite connection configured for reliable operation across local and mounted filesystems."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute("PRAGMA journal_mode = MEMORY;")
            conn.execute("PRAGMA synchronous = OFF;")
            yield conn

    def execute_script(self, sql_script_path: Path) -> None:
        """Execute a multi-statement SQL script file."""
        if not sql_script_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_script_path}")
        sql_content = sql_script_path.read_text(encoding="utf-8")
        with self._connect() as conn:
            conn.executescript("PRAGMA journal_mode = MEMORY; PRAGMA synchronous = OFF;\n" + sql_content)
            conn.commit()
        logger.info(f"Executed SQL script: {sql_script_path.name}")

    def drop_existing_objects(self) -> None:
        """Drop views and tables so every rebuild starts from the canonical schema."""
        with self._connect() as conn:
            cur = conn.cursor()
            for view in POWERBI_VIEWS:
                cur.execute(f"DROP VIEW IF EXISTS {view}")
            for table in reversed(CORE_TABLES):  # children before parents
                cur.execute(f"DROP TABLE IF EXISTS {table}")
            conn.commit()

    def initialize_schema(self) -> None:
        """Rebuild the normalized relational tables from sql/schema.sql."""
        self.drop_existing_objects()
        self.execute_script(SQL_DIR / "schema.sql")

    def load_processed_tables(self) -> None:
        """Append processed CSV rows into the schema-created tables and verify row counts."""
        with self._connect() as conn:
            for table in CORE_TABLES:
                csv_path = PROCESSED_DATA_DIR / f"{table}.csv"
                if not csv_path.exists():
                    logger.warning(f"Missing processed table file: {csv_path}")
                    continue
                df = pd.read_csv(csv_path)
                df.to_sql(table, con=conn, if_exists="append", index=False)
                stored = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                if stored != len(df):
                    raise RuntimeError(f"Row count mismatch for '{table}': CSV has {len(df)}, database has {stored}.")
                logger.info(f"Loaded {stored} rows into SQL table '{table}'.")
            conn.commit()

    def create_powerbi_views(self) -> None:
        """Execute Power BI star-schema view definitions."""
        self.execute_script(SQL_DIR / "powerbi_views.sql")

    def export_powerbi_star_schema(self) -> None:
        """Export star-schema views to CSV and multi-sheet Excel workbook in data/powerbi_export/."""
        ensure_directories()
        xlsx_path = POWERBI_DATA_DIR / "Ecommerce_Star_Schema.xlsx"
        with self._connect() as conn:
            with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
                for view_name in POWERBI_VIEWS:
                    df = pd.read_sql_query(f"SELECT * FROM {view_name};", con=conn)
                    out_file = POWERBI_DATA_DIR / f"{view_name}.csv"
                    df.to_csv(out_file, index=False)
                    df.to_excel(writer, sheet_name=view_name, index=False)
                    logger.info(f"Exported Power BI view {view_name}: {out_file} ({len(df)} rows)")
        logger.info(f"Exported consolidated Power BI Star Schema workbook: {xlsx_path}")
        build_powerbi_package_zip()

    def query(self, sql_query: str) -> pd.DataFrame:
        """Run an analytical query and return a DataFrame."""
        with self._connect() as conn:
            return pd.read_sql_query(sql_query, con=conn)


def build_powerbi_package_zip(target_zip_path: Optional[Path] = None) -> Path:
    """Bundle the 7 Star-Schema tables, Excel model, DAX measures, mockup and pbip into a zip package."""
    ensure_directories()
    target = Path(target_zip_path or (POWERBI_DATA_DIR / "Ecommerce_PowerBI_Package.zip"))
    powerbi_docs = PROJECT_ROOT / "powerbi"

    files = [
        (POWERBI_DATA_DIR / "Ecommerce_Star_Schema.xlsx", "Ecommerce_Star_Schema.xlsx"),
        (POWERBI_DATA_DIR / "DimCustomer.csv", "tables/DimCustomer.csv"),
        (POWERBI_DATA_DIR / "DimProduct.csv", "tables/DimProduct.csv"),
        (POWERBI_DATA_DIR / "DimCategory.csv", "tables/DimCategory.csv"),
        (POWERBI_DATA_DIR / "DimDate.csv", "tables/DimDate.csv"),
        (POWERBI_DATA_DIR / "FactSales.csv", "tables/FactSales.csv"),
        (POWERBI_DATA_DIR / "FactReviews.csv", "tables/FactReviews.csv"),
        (POWERBI_DATA_DIR / "FactInteractions.csv", "tables/FactInteractions.csv"),
        (powerbi_docs / "dax_measures.md", "dax_measures.md"),
        (powerbi_docs / "powerbi_report_mockup.html", "powerbi_report_mockup.html"),
        (powerbi_docs / "README.md", "README.md"),
        (powerbi_docs / "Ecommerce_Customer_Intelligence.pbip", "Ecommerce_Customer_Intelligence.pbip"),
    ]

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, arc in files:
            if src.exists():
                zf.write(src, arcname=arc)

    logger.info(f"Built consolidated Power BI Package: {target} ({target.stat().st_size:,} bytes)")
    return target


def setup_database_and_export():
    """Orchestrate database rebuild, table loading, view creation and Power BI export."""
    ensure_directories()
    db = DatabaseManager()
    db.initialize_schema()
    db.load_processed_tables()
    db.create_powerbi_views()
    db.export_powerbi_star_schema()
    logger.info("Database and Power BI star-schema exports successfully completed.")


if __name__ == "__main__":
    setup_database_and_export()
