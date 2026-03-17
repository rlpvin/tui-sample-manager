from datetime import datetime
from pathlib import Path


from sample_manager.utils.audio_analysis import analyze_audio


def extract_metadata(path: Path, analyze: bool = False):

    stat = path.stat()

    meta = {
        "filename": path.name,
        "path": str(path),
        "extension": path.suffix.lower().lstrip("."),
        "size": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime),
        "bpm": 0,
        "musical_key": None,
        "duration": 0
    }

    if analyze:
        analysis = analyze_audio(str(path))
        if analysis:
            meta.update({
                "bpm": analysis["bpm"],
                "musical_key": analysis["key"],
                "duration": analysis["duration"]
            })

    return meta