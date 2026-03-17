import librosa
import numpy as np
import os
from pathlib import Path
import warnings
from sample_manager.utils.logging import get_logger

logger = get_logger(__name__)

# Suppress librosa/audioread warnings for clean TUI output
warnings.filterwarnings("ignore")

def is_one_shot(file_path: str, duration: float) -> bool:
    """
    Heuristic to determine if a sample is a one-shot (non-looping).
    Returns True if duration is short OR filename contains one-shot keywords.
    """
    if duration < 2.0:
        return True
    
    filename = os.path.basename(file_path).lower()
    one_shot_keywords = {
        'kick', 'snare', 'clap', 'hit', 'perc', 'tom', 'rim', 
        'hat', 'shaker', 'crash', 'ride', 'one-shot', 'oneshot'
    }
    
    return any(kw in filename for kw in one_shot_keywords)

def analyze_audio(file_path: str):
    """
    Perform deep analysis of an audio file to extract BPM, Key, and Duration.
    """
    if not os.path.exists(file_path):
        logger.warning(f"Analysis failed: File does not exist: {file_path}")
        return None

    logger.debug(f"Starting audio analysis for: {file_path}")

    try:
        # 1. Duration (fastest)
        duration = librosa.get_duration(path=file_path)
        
        # Check if it's a one-shot to skip BPM
        one_shot = is_one_shot(file_path, duration)
        
        # 2. Load audio (only first 30 seconds for performance)
        y, sr = librosa.load(file_path, duration=30)
        
        if len(y) == 0:
            return {
                "bpm": 0,
                "key": "Unknown",
                "duration": round(duration, 2)
            }

        # 3. BPM Detection (Skip for one-shots)
        bpm = 0
        if not one_shot:
            # Use a more robust tempo estimation logic
            # Calculate onset envelope
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            
            # Use beat_track to get a more precise tempo estimate than feature.tempo
            # We use a tighter window for more accuracy
            tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            
            # Safely convert to float
            try:
                bpm_val = float(np.atleast_1d(tempo)[0])
                # Bias towards integer values if it's very close (within 0.5%)
                if abs(bpm_val - round(bpm_val)) < (bpm_val * 0.005):
                    bpm = int(round(bpm_val))
                else:
                    # Otherwise just round
                    bpm = int(round(bpm_val))
            except (IndexError, TypeError, ValueError):
                bpm = 0
                
            # Fallback range check
            if bpm < 30 or bpm > 300:
                bpm = 0

        # 4. Key Detection (Using Chroma Energy Normalized Statistics - CENS)
        # CENS is much more robust to percussive noise and timbre changes
        chroma = librosa.feature.chroma_cens(y=y, sr=sr)
        chroma_avg = np.mean(chroma, axis=1)
        
        # Weighted Krumhansl-Schmuckler profiles (more accurate than simple ones)
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        best_corr = -1
        best_key = "Unknown"
        
        for i in range(12):
            # Shift profiles to match chromatic scale
            major_shift = np.roll(major_profile, i)
            minor_shift = np.roll(minor_profile, i)
            
            # Standard Pearson correlation
            major_corr = np.corrcoef(chroma_avg, major_shift)[0, 1]
            minor_corr = np.corrcoef(chroma_avg, minor_shift)[0, 1]
            
            if major_corr > best_corr:
                best_corr = major_corr
                best_key = f"{keys[i]} Major"
            if minor_corr > best_corr:
                best_corr = minor_corr
                best_key = f"{keys[i]} Minor"

        result = {
            "bpm": bpm,
            "key": best_key,
            "duration": round(duration, 2)
        }
        logger.debug(f"Analysis complete for {os.path.basename(file_path)}: {result}")
        return result

    except Exception as e:
        logger.error(f"Error analyzing audio {file_path}: {e}", exc_info=True)
        # Fallback for unsupported files or errors
        return {
            "bpm": 0,
            "key": "Error",
            "duration": 0
        }
