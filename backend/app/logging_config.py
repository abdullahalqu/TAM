"""
Centralized Logging Configuration
Structured logging for easy integration with Loki, Grafana, ELK, etc.
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import os


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    Compatible with Loki, Grafana, Elasticsearch, etc.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Standard LogRecord attributes to exclude from extra fields
        standard_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
            'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname', 'process',
            'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info',
            'exc_text', 'stack_info', 'getMessage', 'taskName'
        }

        # Automatically add all custom extra fields
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith('_'):
                log_data[key] = value

        # Environment info
        log_data["environment"] = os.getenv("ENVIRONMENT", "development")
        log_data["service"] = "task-management-api"

        return json.dumps(log_data)


class StandardFormatter(logging.Formatter):
    """
    Human-readable formatter for development
    """

    def format(self, record: logging.LogRecord) -> str:
        # Color codes for terminal
        colors = {
            'DEBUG': '\033[36m',     # Cyan
            'INFO': '\033[32m',      # Green
            'WARNING': '\033[33m',   # Yellow
            'ERROR': '\033[31m',     # Red
            'CRITICAL': '\033[35m',  # Magenta
        }
        reset = '\033[0m'

        level_color = colors.get(record.levelname, '')
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        log_message = (
            f"{level_color}[{timestamp}] "
            f"{record.levelname:8s}{reset} "
            f"[{record.name}] "
            f"{record.getMessage()}"
        )

        if record.exc_info:
            log_message += f"\n{self.formatException(record.exc_info)}"

        return log_message


def setup_logging(log_level: str = None, use_json: bool = None) -> logging.Logger:
    """
    Configure application logging

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Use JSON formatter (True) or human-readable (False)

    Returns:
        Configured logger instance
    """
    # Get config from environment or defaults
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    if use_json is None:
        # Use JSON in production, human-readable in development
        use_json = os.getenv("LOG_FORMAT", "json").lower() == "json"

    # Create root logger
    logger = logging.getLogger("task_management")
    logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))

    # Set formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = StandardFormatter()

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Don't propagate to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module

    Usage:
        logger = get_logger(__name__)
        logger.info("Something happened")
    """
    return logging.getLogger(f"task_management.{name}")


# Initialize default logger
logger = setup_logging()


# Example usage and helper functions
def log_request(method: str, endpoint: str, status_code: int, duration_ms: float, user_id: str = None):
    """Helper to log HTTP requests with structured data"""
    extra = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }
    if user_id:
        extra["user_id"] = user_id

    logger.info(f"{method} {endpoint} - {status_code}", extra=extra)


def log_job(job_name: str, job_id: str, status: str, duration_ms: float = None):
    """Helper to log background jobs"""
    extra = {
        "job_name": job_name,
        "job_id": job_id,
        "status": status,
    }
    if duration_ms:
        extra["duration_ms"] = duration_ms

    logger.info(f"Job {job_name} [{job_id}] - {status}", extra=extra)
