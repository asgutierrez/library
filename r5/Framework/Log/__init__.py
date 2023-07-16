import logging

from r5.Framework.Helpers import Environment

# Get Log Level
LOG = Environment.var_get("R5_LOG", False)


def setup_logger(log_format=None):
    """Setup Logger"""
    if not log_format:
        log_format = "[%(processName)s] [%(levelname)s %(asctime)-15s] - [%(filename)s:%(lineno)d:%(funcName)s] - %(message)s"

    if not LOG:
        return

    logging.basicConfig(level=LOG.upper(), format=log_format)


def get_logger(name=None):
    """Return Logger"""
    if not name:
        return logging.getLogger()
    return logging.getLogger(name)
