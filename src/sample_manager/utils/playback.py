import os
import platform
import signal
import subprocess

from sample_manager.utils.logging import get_logger

logger = get_logger(__name__)


class Player:
    def __init__(self):
        self.process = None

    def play(self, path: str) -> bool:
        """
        Play an audio file using system utilities.
        """
        self.stop()

        if not os.path.exists(path):
            logger.error(f"File not found: {path}")
            return False

        system = platform.system()
        if system == "Darwin":
            cmd = ["afplay", path]
        elif system == "Linux":
            # Try aplay, then play (sox)
            cmd = ["aplay", "-q", path]
        else:
            cmd = ["play", "-q", path]

        try:
            # We use start_new_session to ensure it doesn't get signals
            # intended for the TUI
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid if system != "Windows" else None,
            )
            return True
        except FileNotFoundError:
            # If the primary command fails, try 'play' as fallback
            if cmd[0] != "play":
                try:
                    self.process = subprocess.Popen(
                        ["play", "-q", path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return True
                except FileNotFoundError:
                    pass
            logger.error(f"Playback utility not found: {cmd[0]}")
            return False
        except Exception as e:
            logger.error(f"Playback error: {e}")
            return False

    def stop(self):
        """
        Stop current playback.
        """
        if self.process and self.process.poll() is None:
            try:
                # Send SIGTERM to the process group
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except Exception:
                self.process.terminate()
            self.process.wait()
        self.process = None

    def is_playing(self) -> bool:
        return self.process is not None and self.process.poll() is None
