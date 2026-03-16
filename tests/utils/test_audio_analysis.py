import os
import numpy as np
import pytest
from scipy.io import wavfile
from sample_manager.utils.audio_analysis import analyze_audio

@pytest.fixture
def synthetic_wav(tmp_path):
    # Generate a 1-second 440Hz sine wave
    sr = 22050
    t = np.linspace(0, 1, sr)
    # Adding a simple pulse to help with tempo detection (not real tempo but ensures no error)
    y = np.sin(2 * np.pi * 440 * t)
    
    file_path = tmp_path / "test.wav"
    wavfile.write(file_path, sr, y.astype(np.float32))
    return str(file_path)

def test_analyze_audio_duration(synthetic_wav):
    analysis = analyze_audio(synthetic_wav)
    assert analysis is not None
    assert analysis["duration"] == 1.0

def test_analyze_audio_bpm_one_shot_duration(synthetic_wav):
    # The synthetic_wav is 1s, so it should be detected as a one-shot (BPM=0)
    analysis = analyze_audio(synthetic_wav)
    assert analysis["bpm"] == 0

def test_analyze_audio_keyword_exclusion(tmp_path):
    # Long duration but "kick" in name
    sr = 22050
    t = np.linspace(0, 5, sr * 5)
    y = np.sin(2 * np.pi * 440 * t)
    file_path = tmp_path / "heavy_kick_loop.wav"
    wavfile.write(file_path, sr, y.astype(np.float32))
    
    analysis = analyze_audio(str(file_path))
    assert analysis["bpm"] == 0

def test_analyze_audio_loop_bpm(tmp_path):
    # Generate a 120 BPM pulse loop (5 seconds)
    sr = 22050
    duration = 5.0
    t = np.linspace(0, duration, int(sr * duration))
    y = np.zeros_like(t)
    # Beats every 0.5s (120 BPM)
    for i in range(10):
        y[int(i * 0.5 * sr) : int(i * 0.5 * sr + 500)] = 1.0
        
    file_path = tmp_path / "drum_loop_120.wav"
    wavfile.write(file_path, sr, y.astype(np.float32))
    
    analysis = analyze_audio(str(file_path))
    assert analysis["bpm"] > 0
    # Allow some tolerance for librosa tempo estimation
    assert 110 <= analysis["bpm"] <= 130

def test_analyze_audio_key(synthetic_wav):
    analysis = analyze_audio(synthetic_wav)
    assert "key" in analysis
    assert analysis["key"] != "Unknown"
    # A 440Hz sine wave should be an 'A'
    assert "A" in analysis["key"]

def test_analyze_audio_nonexistent():
    analysis = analyze_audio("nonexistent.wav")
    assert analysis is None
