import os
import sys
import click
from sample_manager.app.tui import SampleManagerApp
from sample_manager.utils.logging import setup_logging
from sample_manager.db.migrate import run_migrations

@click.command()
@click.version_option(version="0.1.0")
@click.option("--debug", is_flag=True, help="Enable debug logging.")
def main(debug):
    """
    TUI Sample Manager - Organize and audition your audio samples from the terminal.
    """
    # 1. Setup Logging
    if debug:
        os.environ["LOG_LEVEL"] = "DEBUG"
    setup_logging()
    
    # 2. Ensure DB is up to date
    try:
        run_migrations()
    except Exception as e:
        print(f"Error initializing database: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 3. Launch App
    try:
        app = SampleManagerApp()
        app.run()
    except Exception as e:
        print(f"Application crash: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
