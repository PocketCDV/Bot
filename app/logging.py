import logging

from config import config

# Main Logger instance.
logger = logging.getLogger("pocketcdv")
logger.setLevel(config.log_level)
