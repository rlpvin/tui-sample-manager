import os
import tomllib
from pathlib import Path
from platformdirs import user_config_dir, user_data_dir

APP_NAME = "tui-sample-manager"
CONFIG_DIR = Path(user_config_dir(APP_NAME))
CONFIG_PATH = CONFIG_DIR / "settings.toml"

def get_default_config():
    """Return a default configuration dictionary."""
    data_dir = user_data_dir(APP_NAME)
    return {
        "database": {
            "path": str(Path(data_dir) / "samples.db")
        },
        "directories": []
    }

def ensure_config():
    """Ensure configuration file exists, creating it with defaults if necessary."""
    if not CONFIG_PATH.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config = get_default_config()
        
        # In a real app, we'd write this to the file
        import tomllib
        # Since we only have tomllib (read-only in 3.11+), we'll do simple string writing 
        # or just return the dict. But let's actually write a basic version.
        try:
            with open(CONFIG_PATH, "w") as f:
                f.write("[database]\n")
                f.write(f'path = "{config["database"]["path"]}"\n')
                f.write("\n[directories]\n")
        except Exception:
            pass # Fallback to dict if writing fails
        return config
    return None

def load_config():
    """Load application configuration from TOML file."""
    # 1. Check current directory (for local dev)
    local_path = Path("config/settings.toml")
    if local_path.exists():
        with open(local_path, "rb") as f:
            return tomllib.load(f)

    # 2. Check user config dir
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "rb") as f:
            return tomllib.load(f)
            
    # 3. Create and return defaults
    ensure_config()
    return get_default_config()
