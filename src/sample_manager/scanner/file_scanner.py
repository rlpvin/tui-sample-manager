from pathlib import Path

SUPPORTED_FORMATS = {".wav", ".mp3", ".aiff", ".aif", ".flac"}


def is_supported_audio_file(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_FORMATS


def scan_directory(directory: str):
    """
    Recursively scan directory for supported audio files.
    """

    base = Path(directory)

    for path in base.resolve().rglob("*"):

        if not path.is_file():
            continue

        if is_supported_audio_file(path):
            yield path
