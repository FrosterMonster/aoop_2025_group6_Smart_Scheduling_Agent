"""Logging configuration utilities"""

import logging
import os
import re
from logging.handlers import RotatingFileHandler
from ai_schedule_agent.config.manager import ConfigManager


class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from logs (API keys, tokens, credentials)"""

    # Patterns for sensitive data
    SENSITIVE_PATTERNS = [
        (re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]+)(["\']?)', re.IGNORECASE), r'\1***REDACTED***\3'),
        (re.compile(r'(token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-\.]+)(["\']?)', re.IGNORECASE), r'\1***REDACTED***\3'),
        (re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'\s]+)(["\']?)', re.IGNORECASE), r'\1***REDACTED***\3'),
        (re.compile(r'(secret["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]+)(["\']?)', re.IGNORECASE), r'\1***REDACTED***\3'),
        (re.compile(r'Bearer\s+[a-zA-Z0-9_\-\.]+', re.IGNORECASE), 'Bearer ***REDACTED***'),
        (re.compile(r'sk-[a-zA-Z0-9]{20,}', re.IGNORECASE), 'sk-***REDACTED***'),  # OpenAI keys
    ]

    def filter(self, record):
        """Redact sensitive data from log messages"""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)

        # Also check args
        if hasattr(record, 'args') and record.args:
            try:
                sanitized_args = []
                for arg in record.args:
                    if isinstance(arg, str):
                        sanitized_arg = arg
                        for pattern, replacement in self.SENSITIVE_PATTERNS:
                            sanitized_arg = pattern.sub(replacement, sanitized_arg)
                        sanitized_args.append(sanitized_arg)
                    else:
                        sanitized_args.append(arg)
                record.args = tuple(sanitized_args)
            except Exception:
                pass  # If we can't sanitize args, leave them as is

        return True


def setup_logging():
    """Setup application logging with rotating file handler and sensitive data filtering"""
    config = ConfigManager()

    # Get log level from environment or config
    log_level_str = os.getenv('LOG_LEVEL', config.get_setting('logging', 'level', default='INFO'))
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    log_format = config.get_setting('logging', 'format', default='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Create handlers list
    handlers = []

    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    handlers.append(console_handler)

    # Rotating file handler (if enabled)
    if config.get_setting('logging', 'file_enabled', default=True):
        log_dir = config.get_path('logs_directory', '.config/logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')

        # Rotating file handler: max 1MB per file, keep 5 backup files
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1_000_000,  # 1MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(SensitiveDataFilter())
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
        force=True  # Override any existing configuration
    )

    # Create and return logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized - Level: %s, Handlers: %d", log_level_str.upper(), len(handlers))

    return logger


# Create module-level logger
logger = setup_logging()
