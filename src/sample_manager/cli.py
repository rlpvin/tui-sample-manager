"""
CLI entry point for the TUI Sample Manager.
"""
from sample_manager.scanner.directories import register_directory
from sample_manager.scanner.indexer import reindex
from sample_manager.config import load_config
from sample_manager.db.init_db import initialize_database
from sample_manager.db.migrate import run_migrations
from sample_manager.logger import setup_logging


def main():

    logger = setup_logging()

    config = load_config()

    initialize_database()
    run_migrations()

    logger.info("TUI Sample Manager starting...")
    logger.info(f"Loaded configuration: {config}")

    print("TUI Sample Manager started successfully.")

    import sys

    if len(sys.argv) > 2 and sys.argv[1] == "add-dir":
        register_directory(sys.argv[2])
        print("Directory registered.")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "scan":
        reindex()
        print("Scan completed.")
        return
