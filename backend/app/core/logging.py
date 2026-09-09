"""Logging configuration for FactLens."""
import logging
import sys
from app.core.config import settings


def setup_logging():
    """Setup structured application logging."""
    log_format = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger("factlens")


logger = setup_logging()
