import json
import logging
from typing import Any, Dict

# Loading log config as a Dict.
with open("app/asgi/logging.json", "r", encoding="utf-8") as f:
    API_LOG_CONFIG: Dict[str, Any] = json.load(f)


logger: logging.Logger = logging.getLogger("pocketcdv_backend")
