#!/usr/bin/env python3
"""Lead Generator Standalone - Entry Point.

Single-user desktop application for email marketing campaigns.
"""

import os
import sys
import logging
import yaml
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.database import init_database, Database


def setup_logging() -> None:
    """Configure logging for the application."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(PROJECT_ROOT / "data" / "app.log", mode='a')
        ]
    )


def load_config() -> dict:
    """Load configuration from config.yaml."""
    config_path = PROJECT_ROOT / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def ensure_data_directory() -> None:
    """Ensure data directory exists."""
    data_dir = PROJECT_ROOT / "data"
    files_dir = data_dir / "files"

    data_dir.mkdir(exist_ok=True)
    files_dir.mkdir(exist_ok=True)


def main() -> None:
    """Main application entry point."""
    # Setup logging first
    ensure_data_directory()
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting Lead Generator Standalone...")

    # Load configuration
    config = load_config()
    logger.info("Configuration loaded")

    # Initialize database
    db_path = config.get('data', {}).get('database_path', 'data/leadgen.db')
    if not os.path.isabs(db_path):
        db_path = str(PROJECT_ROOT / db_path)

    Database.set_path(db_path)
    init_database(db_path)
    logger.info(f"Database initialized at {db_path}")

    # Import UI after database is ready
    try:
        from ui.app import MainApplication
        app = MainApplication(config)
        app.run()
    except ImportError as e:
        logger.error(f"Failed to import UI module: {e}")
        logger.info("Running in headless mode (UI not available)")
        print("Lead Generator Standalone")
        print("=" * 40)
        print("UI module not available. Database has been initialized.")
        print(f"Database location: {db_path}")
        print("\nTo use the application, ensure ttkbootstrap is installed:")
        print("  pip install ttkbootstrap")


if __name__ == "__main__":
    main()
