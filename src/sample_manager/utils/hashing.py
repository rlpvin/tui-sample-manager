import hashlib


def calculate_hash(path: str, chunk_size: int = 8192) -> str:
    """
    Calculate the SHA-256 hash of a file.
    """
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, IOError):
        return ""
