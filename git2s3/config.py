import logging
import os
from datetime import datetime

from git2s3.models import LogOptions


def default_logger(log: LogOptions) -> logging.Logger:
    """Generates a default console logger.

    Args:
        log: Log option chosen by the user.

    Returns:
        logging.Logger:
        Logger object.
    """
    if log == LogOptions.file:
        if not os.path.isdir("logs"):
            os.mkdir("logs")
        logfile: str = datetime.now().strftime(
            os.path.join("logs", "pyfilebrowser_%d-%m-%Y.log")
        )
        handler = logging.FileHandler(filename=logfile)
    else:
        handler = logging.StreamHandler()
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler.setFormatter(
        fmt=logging.Formatter(
            fmt="%(asctime)s - %(levelname)-8s - [%(funcName)s:%(lineno)d] - %(message)s"
        )
    )
    logger.addHandler(hdlr=handler)
    return logger
