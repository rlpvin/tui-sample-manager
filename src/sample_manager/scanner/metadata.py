from pathlib import Path
from datetime import datetime


def extract_metadata(path: Path):

    stat = path.stat()

    return {
        "filename": path.name,
        "path": str(path),
        "extension": path.suffix.lower().lstrip("."),
        "size": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime),
    }