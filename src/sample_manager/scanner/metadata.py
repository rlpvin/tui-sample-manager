from datetime import datetime
from pathlib import Path


def extract_metadata(path: Path):

    stat = path.stat()

    return {
        "filename": path.name,
        "path": str(path),
        "extension": path.suffix.lower().lstrip("."),
        "size": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime),
    }