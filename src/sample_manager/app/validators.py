from pathlib import Path


def validate_directory(path: str):

    p = Path(path).expanduser()

    if not p.exists():
        raise ValueError(f"Directory does not exist: {path}")

    if not p.is_dir():
        raise ValueError(f"Not a directory: {path}")

    return str(p)
