import logging
import sys
from app.core.config import settings


def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f'Logging configured with level: {settings.LOG_LEVEL}')
    return logger


logger = setup_logging()

