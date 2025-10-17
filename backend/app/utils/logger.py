import logging


def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a logger instance with a specific name. The logger is
    configured to output logs to the console (stdout) with a standardized format
    that includes the timestamp, logger name, log level, and log message.

    Parameters
    ----------
    name : str
        The name of the logger, typically the module or component name.

    Returns
    -------
    logging.Logger
        A logger instance with the specified name and configured format.
    """
    logger = logging.getLogger(name)

    # Ensure we only add one handler
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Set the logging level to DEBUG to capture all logs
        logger.setLevel(logging.DEBUG)

    # Ensure logs propagate to root logger if needed
    logger.propagate = True

    return logger
