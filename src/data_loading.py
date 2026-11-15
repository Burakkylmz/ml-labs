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


# Columns excluded at load time, never read into memory: direct PII (name, email, password,
# street address, zip codes) and raw customer/order-customer identifiers. This is enforced here
# rather than left to notebook discipline, since every LAB reusing this loader inherits the
# guarantee automatically.
DATACO_PII_COLUMNS = [
    "Customer Email",
    "Customer Password",
    "Customer Fname",
    "Customer Lname",
    "Customer Street",
    "Customer Zipcode",
    "Order Zipcode",
    "Customer Id",
    "Order Customer Id",
]


def load_dataco_supply_chain(config: dict) -> pd.DataFrame:
    """Load the DataCo Supply Chain dataset, excluding PII columns at read time.

    The raw CSV is latin-1 encoded (not UTF-8); reading with the wrong encoding raises
    UnicodeDecodeError.
    """
    csv_path = get_project_root() / config["data"]["dataco_supply_chain"]
    csv_path = require_file(csv_path)
    header = pd.read_csv(csv_path, encoding="latin-1", nrows=0).columns.tolist()
    safe_columns = [c for c in header if c not in DATACO_PII_COLUMNS]
    return pd.read_csv(csv_path, encoding="latin-1", usecols=safe_columns)
