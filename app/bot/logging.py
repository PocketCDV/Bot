import logging

from config import config

# Main Logger instance.
logger = logging.getLogger("pocketcdv_bot")
logger.setLevel(config.log_level)
