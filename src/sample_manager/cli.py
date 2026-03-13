"""
CLI entry point for the TUI Sample Manager.
"""

from sample_manager.config import load_config
from sample_manager.logger import setup_logging


def main():
    logger = setup_logging()

    config = load_config()

    logger.info("TUI Sample Manager starting...")
    logger.info(f"Loaded configuration: {config}")

    print("TUI Sample Manager started successfully.")
