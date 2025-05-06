import logging
from loguru import logger


class InterceptHandler(logging.Handler):
    """
    A custom logging handler that intercepts log messages and prints them to the console.
    """

    def emit(self, record):
        try:
            # Get the log message and level

            level = record.levelname

        except ValueError:
            level = record.levelno
        #  # Get the logger name and message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())