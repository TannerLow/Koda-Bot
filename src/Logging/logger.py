import logging
import sys
import os
from typing import Optional

class Logger:

    def __init__(self, name: str, level: str = "info", *, file: Optional[str] = None):
        if os.path.exists(name):
            name = os.path.basename(name)
        levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "error": logging.ERROR
        }
        level = levels[level.lower().strip()]
        format: str = "%(asctime)s [%(levelname)s][%(name)s]: %(message)s"

        if file:
            logging.basicConfig(
                stream=file,
                level=level,
                format=format
            )
        else:
            logging.basicConfig(
                stream=sys.stdout,  # Send logs to stdout instead of stderr
                level=level,
                format=format
            )

        self.logger = logging.getLogger(name)

    def info(self, log_message: str) -> None:
        self.logger.info(log_message)

    def debug(self, log_message: str) -> None:
        self.logger.debug(log_message)
    
    def error(self, log_message: str) -> None:
        self.logger.error(log_message)
