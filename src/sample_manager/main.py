from sample_manager.config import load_config
from sample_manager.logger import setup_logging


def main():
    """Application entry point."""

    logger = setup_logging()

    config = load_config()

    logger.info("TUI Sample Manager starting...")
    logger.info(f"Loaded configuration: {config}")

    print("TUI Sample Manager started successfully.")


if __name__ == "__main__":
    main()
