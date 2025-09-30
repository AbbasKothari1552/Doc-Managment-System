import logging
import sys
from pathlib import Path
from datetime import datetime

from app.core.settings import settings

# Create logs directory if it doesn't exist
settings.LOG_DIR.mkdir(exist_ok=True)

# Current date for log filename
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = settings.LOG_DIR / f"dms_{CURRENT_DATE}.log"

# Basic configuration
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    return logger