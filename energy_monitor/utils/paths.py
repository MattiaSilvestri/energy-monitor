import json
import os
from importlib.resources import files
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir

APP_NAME = "energy-monitor"

# Read-only files shipped inside the package
PACKAGE_ROOT = files("energy_monitor")
DEFAULT_CONFIG = PACKAGE_ROOT / "config" / "config.yml"
BUNDLED_DATA = PACKAGE_ROOT / "data"


def config_dir() -> Path:
    """User-writable folder for configuration files (e.g. ~/.config/energy-monitor)."""
    path = Path(user_config_dir(APP_NAME, appauthor=False))
    path.mkdir(parents=True, exist_ok=True)
    return path


def data_dir() -> Path:
    """User-writable folder for cached data (e.g. ~/.local/share/energy-monitor)."""
    path = Path(user_data_dir(APP_NAME, appauthor=False))
    path.mkdir(parents=True, exist_ok=True)
    return path


def secrets_file() -> Path:
    return config_dir() / "secrets.yml"


def user_data_file() -> Path:
    return data_dir() / "user_data.json"


def load_user_data() -> dict:
    fname = user_data_file()
    if not fname.is_file():
        return {}
    try:
        with open(fname, "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def update_user_data(**values) -> None:
    user_data = load_user_data()
    user_data.update(values)
    with open(user_data_file(), "w") as f:
        json.dump(user_data, f)


def cpu_database_file(cpu_brand: str) -> Path:
    return data_dir() / f"database_{cpu_brand}.json"


def bundled_cpu_database(cpu_brand: str):
    return BUNDLED_DATA / f"database_{cpu_brand}.json"


def user_config_file():
    """Return the config installed by the user with --install-config, if any, else the default one."""
    custom = load_user_data().get("user_config")
    if custom and os.path.isfile(custom):
        return Path(custom)
    return DEFAULT_CONFIG
