""" Pywinman starter"""
import logging
import logging.config
from singleton import Singleton
from monitorsholder import MonitorHolder
from windows_holder import WindowsHolder


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            'format': '[%(levelname)s:%(asctime)s][%(name)s] %(message)s'
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
        },
    },

    'loggers': {
        '': {  # root logger
            'handlers': ['stream_handler'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}



if __name__ == "__main__":
    logging.config.dictConfig(LOGGING_CONFIG)
    LOG = logging.getLogger(__name__)
    if Singleton().is_already_running():
        LOG.debug("Pywinman is already running")
        exit()
    LOG.warning("Starting Pywinman")
    MonitorHolder()
    WindowsHolder()
else:
    exit()
