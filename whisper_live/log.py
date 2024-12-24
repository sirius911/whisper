import logging

CONTAINER = 1

log_levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.critical
    }

LOG_LEVEL = logging.getLogger("WhisperLive")
LOG_LEVEL.setLevel(logging.WARNING)
