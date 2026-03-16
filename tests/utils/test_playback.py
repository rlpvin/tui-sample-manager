import pytest
from unittest.mock import MagicMock, patch
import os
from sample_manager.utils.playback import Player

def test_player_play_stop():
    player = Player()
    
    with patch("subprocess.Popen") as mock_popen:
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        # Mock os.path.exists to always return True for this test
        with patch("os.path.exists", return_value=True):
            # Try playing a fake file
            player.play("/fake/path.wav")
            
            assert mock_popen.called
            assert player.is_playing()
            
            # Stop it
            with patch("os.killpg") as mock_killpg:
                with patch("os.getpgid", return_value=123):
                    player.stop()
                    assert mock_killpg.called or mock_process.terminate.called
                    assert not player.is_playing()

def test_player_file_not_found():
    player = Player()
    with patch("os.path.exists", return_value=False):
        assert player.play("/missing.wav") is False
        assert not player.is_playing()
