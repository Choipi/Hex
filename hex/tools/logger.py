import logging
from enum import Enum


class LogLevel(Enum):
    """Enumeration for log levels.

    - 'DEBUG' prints all log levels when passed in the command line.
    - 'INFO' (verbose) prints all log levels except 'DEBUG'.
    - 'WARNING', 'ERROR' and 'CRITICAL' always print to the terminal.
    """
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


def setup_logging_level(log_level: str):
    """Determine the logging level depending on the option from the command
    line.

    Args
    ----
    log_level : str
        The log level from the command line

    Raises
    ------
    RuntimeError
        if an unknown log level is given
    """
    match log_level:
        case '-v' | '--verbose':
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                # using force=True in case we use log before calling this setup
                force=True)
        case '-d' | '--debug':
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s",
                force=True)
        case _:
            raise RuntimeError(f"Unknown logging level '{log_level}'.")


def log(log_type: LogLevel, message: str):
    """ Prints a message depending on the log level.

    Parameters
    ----------
    log_type : LogLevel
         The level of logging.
    message : str
        The message to log.
    """
    # this basicConfig is used only if setup_logging_level is never
    # called before
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s")

    match log_type:
        case LogLevel.DEBUG:
            logging.debug(message)
        case LogLevel.INFO:
            logging.info(message)
        case LogLevel.WARNING:
            logging.warning(message)
        case LogLevel.ERROR:
            logging.error(message)
        case LogLevel.CRITICAL:
            logging.critical(message)
