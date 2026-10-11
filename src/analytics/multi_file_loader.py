"""
src/analytics/multi_file_loader.py
Multi-file and folder ingestion service supporting batch uploads, ZIP archives,
local directory scanning, schema compatibility checking, and smart merging.
"""
import io
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import zipfile
import pandas as pd

from src.utils.logging import get_logger

logger = get_logger("multi_file_loader")


def read_tabular_file(file_bytes_or_path: Union[bytes, str, Path, io.BytesIO], filename: str) -> pd.DataFrame:
    """Read a CSV or Excel file from bytes or path."""
    filename_low = filename.lower()
    if filename_low.endswith(".csv"):
        if isinstance(file_bytes_or_path, (str, Path)):
            return pd.read_csv(file_bytes_or_path)
        else:
            if isinstance(file_bytes_or_path, bytes):
                file_bytes_or_path = io.BytesIO(file_bytes_or_path)
            return pd.read_csv(file_bytes_or_path)
    elif filename_low.endswith((".xlsx", ".xls")):
        if isinstance(file_bytes_or_path, (str, Path)):
            return pd.read_excel(file_bytes_or_path)
        else:
            if isinstance(file_bytes_or_path, bytes):
                file_bytes_or_path = io.BytesIO(file_bytes_or_path)
            return pd.read_excel(file_bytes_or_path)
    else:
        raise ValueError(f"Unsupported file format: {filename}. Supported formats: .csv, .xlsx, .xls")


def load_zip_archive(zip_input: Union[bytes, io.BytesIO, str, Path]) -> Dict[str, pd.DataFrame]:
    """
    Extract and load all valid CSV and Excel files from a ZIP archive.
    Returns a dictionary of {filename: DataFrame}.
    """
    tables: Dict[str, pd.DataFrame] = {}
    if isinstance(zip_input, bytes):
        zip_input = io.BytesIO(zip_input)

    with zipfile.ZipFile(zip_input, "r") as zf:
        for file_info in zf.infolist():
            if file_info.is_dir() or file_info.filename.startswith("__MACOSX") or file_info.filename.startswith("."):
                continue
            name_low = file_info.filename.lower()
            if name_low.endswith((".csv", ".xlsx", ".xls")):
                base_name = Path(file_info.filename).name
                with zf.open(file_info) as f:
                    file_bytes = f.read()
                    try:
                        df = read_tabular_file(file_bytes, base_name)
                        tables[base_name] = df
                    except Exception as e:
                        logger.warning(f"Could not parse {base_name} from ZIP: {e}")

    return tables


def scan_local_directory(folder_path: Union[str, Path]) -> Dict[str, pd.DataFrame]:
    """
    Scan a local folder on disk for CSV and Excel files.
    Returns a dictionary of {filename: DataFrame}.
    """
    path = Path(folder_path).resolve()
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Directory not found: {folder_path}")

    tables: Dict[str, pd.DataFrame] = {}
    for item in sorted(path.iterdir()):
        if item.is_file() and item.name.lower().endswith((".csv", ".xlsx", ".xls")):
            try:
                df = read_tabular_file(item, item.name)
                tables[item.name] = df
            except Exception as e:
                logger.warning(f"Could not load {item.name}: {e}")

    return tables


def check_schema_compatibility(tables: Dict[str, pd.DataFrame]) -> Tuple[bool, List[str]]:
    """
    Check if multiple tables have identical or highly compatible columns (>80% overlap).
    Returns (is_compatible, shared_columns).
    """
    if not tables:
        return False, []

    table_list = list(tables.values())
    if len(table_list) == 1:
        return True, list(table_list[0].columns)

    first_cols = set(c.lower().strip() for c in table_list[0].columns)
    shared_cols = first_cols.copy()

    for df in table_list[1:]:
        curr_cols = set(c.lower().strip() for c in df.columns)
        shared_cols = shared_cols.intersection(curr_cols)

    # Compatible if shared columns represent at least 70% of first table columns
    is_compatible = len(shared_cols) >= max(1, int(len(first_cols) * 0.70))
    return is_compatible, sorted(list(shared_cols))


def combine_homogeneous_tables(tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Concatenate multiple compatible tables into a single master DataFrame,
    adding a '_source_file' column for auditability and provenance.
    """
    dfs_to_concat = []
    for filename, df in tables.items():
        temp = df.copy()
        temp["_source_file"] = filename
        dfs_to_concat.append(temp)

    if not dfs_to_concat:
        return pd.DataFrame()

    combined = pd.concat(dfs_to_concat, ignore_index=True)
    return combined


def auto_join_relational_tables(tables: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, str]:
    """
    Attempt to join heterogeneous tables if common relational keys exist
    (e.g., customer_id, order_id, product_id, sku).
    Returns (joined_df, join_summary_message).
    """
    if len(tables) < 2:
        first_key = list(tables.keys())[0] if tables else ""
        return tables.get(first_key, pd.DataFrame()), "Single table, no join needed."

    # Identify primary candidate keys
    candidate_keys = ["customer_id", "order_id", "transaction_id", "product_id", "sku", "review_id"]
    
    # Sort tables by row count descending (largest table as primary)
    sorted_tables = sorted(tables.items(), key=lambda kv: len(kv[1]), reverse=True)
    base_name, base_df = sorted_tables[0]
    merged_df = base_df.copy()
    joined_names = [base_name]

    for next_name, next_df in sorted_tables[1:]:
        # Find common key
        common_keys = [k for k in candidate_keys if k in merged_df.columns and k in next_df.columns]
        if not common_keys:
            # Check case-insensitive
            m_low = {c.lower(): c for c in merged_df.columns}
            n_low = {c.lower(): c for c in next_df.columns}
            for k in candidate_keys:
                if k in m_low and k in n_low:
                    common_keys = [(m_low[k], n_low[k])]
                    break

        if common_keys:
            join_key = common_keys[0]
            if isinstance(join_key, tuple):
                left_k, right_k = join_key
                merged_df = merged_df.merge(next_df, left_on=left_k, right_on=right_k, how="left", suffixes=("", f"_{next_name}"))
            else:
                merged_df = merged_df.merge(next_df, on=join_key, how="left", suffixes=("", f"_{next_name}"))
            joined_names.append(next_name)

    summary = f"Successfully joined {len(joined_names)} tables ({', '.join(joined_names)})"
    return merged_df, summary
