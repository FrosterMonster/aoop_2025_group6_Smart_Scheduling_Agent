"""Logging configuration utilities"""

import logging
import os
from ai_schedule_agent.config.manager import ConfigManager


def setup_logging():
    """Setup application logging based on configuration"""
    config = ConfigManager()

    log_level = getattr(logging, config.get_setting('logging', 'level', default='INFO'))
    log_format = config.get_setting('logging', 'format', default='%(asctime)s - %(levelname)s - %(message)s')

    # Configure file logging if enabled
    if config.get_setting('logging', 'file_enabled', default=True):
        log_file = os.path.join(config.get_path('logs_directory', '.config/logs'), 'app.log')
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(level=log_level, format=log_format)

    return logging.getLogger(__name__)


# Create module-level logger
logger = setup_logging()
