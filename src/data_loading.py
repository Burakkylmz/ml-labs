"""Reusable data loading helpers shared across ml-labs notebooks."""

from pathlib import Path

import pandas as pd
import yaml


def get_project_root() -> Path:
    """Return the ml-labs project root, independent of the notebook's cwd."""
    return Path(__file__).resolve().parent.parent


def load_config() -> dict:
    """Load config/settings.yaml as a dictionary."""
    config_path = get_project_root() / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def require_file(path: Path) -> Path:
    """Return path if it exists, otherwise raise a clear, actionable error."""
    if not path.exists():
        raise FileNotFoundError(
            f"Required dataset file not found: {path}\n"
            "This dataset is not auto-downloaded; place it manually before "
            "running the notebook."
        )
    return path


def load_ecommerce_shipping(config: dict) -> pd.DataFrame:
    """Load the E-Commerce Shipping dataset using the path from config."""
    csv_path = get_project_root() / config["data"]["ecommerce_shipping"]
    return pd.read_csv(require_file(csv_path))


def load_northwind_orders(config: dict) -> pd.DataFrame:
    """Load the Northwind orders dataset using the path from config."""
    csv_path = get_project_root() / config["data"]["northwind"]["orders"]
    return pd.read_csv(require_file(csv_path))


def load_king_county_house_sales(config: dict) -> pd.DataFrame:
    """Load the King County House Sales dataset using the path from config."""
    csv_path = get_project_root() / config["data"]["king_county_house_sales"]
    return pd.read_csv(require_file(csv_path))
