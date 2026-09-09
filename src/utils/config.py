"""
src/utils/config.py
Configuration loader and path resolution utility.
"""
from pathlib import Path
from typing import Any, Dict, List
import yaml

# Resolve Project Root Directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def load_config() -> Dict[str, Any]:
    """Load configuration dictionary from YAML file."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found at: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Load parsed config
_CONFIG = load_config()

# Global Constants
RANDOM_SEED: int = _CONFIG.get("project", {}).get("random_seed", 42)

# Directory Paths
RAW_DATA_DIR: Path = PROJECT_ROOT / _CONFIG["paths"]["raw_data_dir"]
PROCESSED_DATA_DIR: Path = PROJECT_ROOT / _CONFIG["paths"]["processed_data_dir"]
POWERBI_DATA_DIR: Path = PROJECT_ROOT / _CONFIG["paths"]["powerbi_data_dir"]
DATABASE_PATH: Path = PROJECT_ROOT / _CONFIG["paths"]["database_path"]
SQL_DIR: Path = PROJECT_ROOT / "sql"

MODELS_SENTIMENT_DIR: Path = PROJECT_ROOT / _CONFIG["paths"]["models_sentiment_dir"]
MODELS_RECOMMENDATION_DIR: Path = PROJECT_ROOT / _CONFIG["paths"]["models_recommendation_dir"]
MODELS_TOPIC_DIR: Path = PROJECT_ROOT / _CONFIG["paths"]["models_topic_dir"]
METRICS_FILE: Path = PROJECT_ROOT / _CONFIG["paths"]["metrics_file"]

# Scales & Settings
SCALE_CUSTOMERS: int = _CONFIG["data_generation"]["num_customers"]
SCALE_PRODUCTS: int = _CONFIG["data_generation"]["num_products"]
SCALE_TRANSACTIONS: int = _CONFIG["data_generation"]["num_transactions"]
SCALE_REVIEWS: int = _CONFIG["data_generation"]["num_reviews"]
SCALE_INTERACTIONS: int = _CONFIG["data_generation"]["num_interactions"]

INTERACTION_WEIGHTS: Dict[str, float] = _CONFIG["interaction_weights"]
HYBRID_WEIGHTS: Dict[str, float] = _CONFIG["recommendation"]["hybrid_weights"]
EVALUATION_K_VALUES: List[int] = _CONFIG["recommendation"]["evaluation_k"]
ASPECT_LIST: List[str] = _CONFIG["aspects"]


def ensure_directories() -> None:
    """Ensure all required directories exist on the filesystem."""
    for directory in [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        POWERBI_DATA_DIR,
        DATABASE_PATH.parent,
        MODELS_SENTIMENT_DIR,
        MODELS_RECOMMENDATION_DIR,
        MODELS_TOPIC_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)
