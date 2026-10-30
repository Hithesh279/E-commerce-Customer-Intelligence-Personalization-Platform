"""
src/analytics/multi_file_loader.py
Multi-file and folder ingestion service supporting batch uploads, ZIP archives,
local directory scanning, schema compatibility checking, and smart merging.
"""
import hashlib
import io
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import zipfile
import pandas as pd
import streamlit as st

from src.utils.config import PROJECT_ROOT
from src.utils.logging import get_logger

logger = get_logger("multi_file_loader")

# Limits that stop a hostile or accidental archive from exhausting memory.
MAX_ZIP_MEMBERS = 100
MAX_ZIP_UNCOMPRESSED_BYTES = 200 * 1024 * 1024

_PARSER_CALL_COUNT = 0


def get_parser_call_count() -> int:
    """Return the total number of physical file/archive parse operations executed."""
    return _PARSER_CALL_COUNT


def reset_parser_call_count() -> None:
    """Reset the parse call counter to zero (useful for testing and benchmarking)."""
    global _PARSER_CALL_COUNT
    _PARSER_CALL_COUNT = 0


def compute_bytes_hash(content: bytes) -> str:
    """Compute SHA-256 hash of a bytes object."""
    return hashlib.sha256(content).hexdigest()


def compute_file_hash(path: Union[str, Path]) -> str:
    """Compute SHA-256 hash of a file on disk."""
    p = Path(path)
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_directory_signature(folder_path: Union[str, Path]) -> str:
    """
    Compute a signature hash for a folder based on its tabular files' names, sizes, and mtimes.
    Allows instant cache validation without re-reading files if contents have not changed.
    """
    raw = Path(folder_path).expanduser()
    p = (raw if raw.is_absolute() else PROJECT_ROOT / raw).resolve()
    if not p.exists() or not p.is_dir():
        return ""
    entries = []
    for item in sorted(p.iterdir()):
        if item.is_file() and item.name.lower().endswith((".csv", ".xlsx", ".xls")):
            stat = item.stat()
            entries.append((item.name, stat.st_size, stat.st_mtime))
    return hashlib.sha256(repr(entries).encode("utf-8")).hexdigest()


@st.cache_data(max_entries=32, show_spinner=False)
def parse_tabular_file_cached(
    _file_bytes: bytes,
    filename: str,
    file_size: int,
    file_hash: str,
) -> pd.DataFrame:
    """
    Cached parser for CSV and Excel files. Keyed by filename, file_size, and file_hash.
    The raw bytes argument starts with an underscore so Streamlit bypasses hashing it directly.
    """
    global _PARSER_CALL_COUNT
    _PARSER_CALL_COUNT += 1
    logger.info(
        f"[PARSER_CALL #{_PARSER_CALL_COUNT}] Parsing '{filename}' "
        f"({file_size:,} bytes, hash={file_hash[:8]})."
    )
    return read_tabular_file(_file_bytes, filename)


@st.cache_data(max_entries=16, show_spinner=False)
def load_zip_archive_cached(
    _zip_bytes: bytes,
    filename: str,
    file_size: int,
    file_hash: str,
) -> Dict[str, pd.DataFrame]:
    """
    Cached extractor and parser for ZIP archives containing tabular datasets.
    Keyed by filename, file_size, and file_hash.
    """
    global _PARSER_CALL_COUNT
    _PARSER_CALL_COUNT += 1
    logger.info(
        f"[PARSER_CALL #{_PARSER_CALL_COUNT}] Extracting and parsing ZIP archive '{filename}' "
        f"({file_size:,} bytes, hash={file_hash[:8]})."
    )
    return load_zip_archive(_zip_bytes)


@st.cache_data(max_entries=16, show_spinner=False)
def scan_local_directory_cached(
    folder_path: str,
    dir_signature: str,
) -> Dict[str, pd.DataFrame]:
    """
    Cached folder scanner for tabular files in local machine directories.
    Keyed by folder_path and dir_signature (hash of file names, sizes, and mtimes).
    """
    global _PARSER_CALL_COUNT
    _PARSER_CALL_COUNT += 1
    logger.info(
        f"[PARSER_CALL #{_PARSER_CALL_COUNT}] Scanning folder '{folder_path}' "
        f"(sig={dir_signature[:8] if dir_signature else 'empty'})."
    )
    return scan_local_directory(folder_path)


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


def load_zip_archive(
    zip_input: Union[bytes, io.BytesIO, str, Path],
    max_members: int = MAX_ZIP_MEMBERS,
    max_uncompressed_bytes: int = MAX_ZIP_UNCOMPRESSED_BYTES,
) -> Dict[str, pd.DataFrame]:
    """
    Extract and load all CSV and Excel files from a ZIP archive.
    Returns {path_inside_archive: DataFrame}. Raises ValueError when the archive exceeds the limits.
    """
    tables: Dict[str, pd.DataFrame] = {}
    if isinstance(zip_input, bytes):
        zip_input = io.BytesIO(zip_input)

    with zipfile.ZipFile(zip_input, "r") as zf:
        members = []
        for info in zf.infolist():
            name = info.filename
            base = Path(name).name
            if info.is_dir() or name.startswith("__MACOSX") or base.startswith("."):
                continue
            if Path(name).is_absolute() or ".." in Path(name).parts:
                continue
            if base.lower().endswith((".csv", ".xlsx", ".xls")):
                members.append(info)

        if len(members) > max_members:
            raise ValueError(f"Archive holds {len(members)} tabular files; the limit is {max_members}.")
        declared_total = sum(info.file_size for info in members)
        if declared_total > max_uncompressed_bytes:
            raise ValueError("Archive is too large once extracted; the limit is "
                             f"{max_uncompressed_bytes // (1024 * 1024)} MB.")

        for info in members:
            base_name = Path(info.filename).name
            with zf.open(info) as f:
                file_bytes = f.read(max_uncompressed_bytes + 1)
            if len(file_bytes) > max_uncompressed_bytes:
                raise ValueError(f"{base_name} expands beyond the allowed size.")
            try:
                tables[info.filename] = read_tabular_file(file_bytes, base_name)
            except Exception as e:
                logger.warning(f"Could not parse {base_name} from ZIP: {e}")

    return tables


def _allowed_scan_roots() -> List[Path]:
    """Folders a local scan may read: the project data directory plus any LOCAL_SCAN_ROOTS entries."""
    roots = [(PROJECT_ROOT / "data").resolve()]
    for part in os.environ.get("LOCAL_SCAN_ROOTS", "").split(os.pathsep):
        if part.strip():
            roots.append(Path(part.strip()).expanduser().resolve())
    return roots


def scan_local_directory(
    folder_path: Union[str, Path],
    allowed_roots: Optional[List[Path]] = None,
) -> Dict[str, pd.DataFrame]:
    """
    Scan a folder for CSV and Excel files. Relative paths resolve against the project root.
    The folder must sit inside an allowed root, so the web app cannot read arbitrary locations.
    Returns {filename: DataFrame}.
    """
    raw = Path(folder_path).expanduser()
    path = (raw if raw.is_absolute() else PROJECT_ROOT / raw).resolve()
    roots = allowed_roots if allowed_roots is not None else _allowed_scan_roots()
    if not any(path == root or root in path.parents for root in roots):
        raise PermissionError(
            f"'{folder_path}' is outside the allowed scan locations. "
            "Set LOCAL_SCAN_ROOTS to add a folder."
        )
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Directory not found: {folder_path}")

    tables: Dict[str, pd.DataFrame] = {}
    for item in sorted(path.iterdir()):
        if item.is_file() and item.name.lower().endswith((".csv", ".xlsx", ".xls")):
            try:
                tables[item.name] = read_tabular_file(item, item.name)
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
    Left-join tables on a shared key column (customer_id, order_id, product_id, sku, ...).

    The largest table is the base. A table is joined only when its key is unique, so the join
    cannot repeat base rows. Skipped tables are named in the returned summary.
    """
    if len(tables) < 2:
        first_key = list(tables.keys())[0] if tables else ""
        return tables.get(first_key, pd.DataFrame()), "Single table, no join needed."

    candidate_keys = ["customer_id", "order_id", "transaction_id", "product_id", "sku", "review_id"]
    sorted_tables = sorted(tables.items(), key=lambda kv: len(kv[1]), reverse=True)
    base_name, base_df = sorted_tables[0]
    merged_df = base_df.copy()
    joined_names = [base_name]
    skipped: List[str] = []

    for next_name, next_df in sorted_tables[1:]:
        join_pair = None
        for k in candidate_keys:
            if k in merged_df.columns and k in next_df.columns:
                join_pair = (k, k)
                break
        if join_pair is None:
            m_low = {c.lower(): c for c in merged_df.columns}
            n_low = {c.lower(): c for c in next_df.columns}
            for k in candidate_keys:
                if k in m_low and k in n_low:
                    join_pair = (m_low[k], n_low[k])
                    break
        if join_pair is None:
            skipped.append(f"{next_name} (no shared key)")
            continue

        left_k, right_k = join_pair
        if next_df[right_k].duplicated().any():
            skipped.append(f"{next_name} ('{right_k}' is not unique there, so joining would repeat rows)")
            continue
        merged_df = merged_df.merge(
            next_df, left_on=left_k, right_on=right_k, how="left", suffixes=("", f"_{next_name}")
        )
        joined_names.append(next_name)

    summary = f"Successfully joined {len(joined_names)} tables ({', '.join(joined_names)})"
    if skipped:
        summary += ". Not joined: " + "; ".join(skipped)
    return merged_df, summary


