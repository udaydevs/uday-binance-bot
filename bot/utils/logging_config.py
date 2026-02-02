"""Global logger initialized here"""
import sys
from loguru import logger

LOG_FILE = "bot.log"


def configure_logs(verbose: bool = False, pipe_to_stderr: bool = True):
    """Takeover process logs and create a logger with Loguru according to the
    configuration."""
    logger.remove()

    level = "DEBUG" if verbose else "INFO"

    pipe = sys.stderr if pipe_to_stderr else sys.stdout
    logger.add(
        pipe,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | <level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    logger.add(
        LOG_FILE,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        backtrace=True,
        diagnose=True,
        rotation=None,
        retention=None,
        compression=None,
    )


def get_logger():
    """Return the logger for all modules."""
    return logger
