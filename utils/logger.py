import logging
import sys


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(handler)
    log_level = logging.INFO
    try:
        from backend.config import settings
        log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    except Exception:
        pass
    logger.setLevel(log_level)
    return logger
