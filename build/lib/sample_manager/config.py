from pathlib import Path

import tomllib

CONFIG_PATH = Path("config/settings.toml")


def load_config():
    """Load application configuration from TOML file."""

    if not CONFIG_PATH.exists():
        raise FileNotFoundError("Configuration file not found.")

    with open(CONFIG_PATH, "rb") as f:
        config = tomllib.load(f)

    return config
