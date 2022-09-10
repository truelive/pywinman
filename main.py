from ctypes import wintypes
import ctypes as ct
from singleton import Singleton
from monitorsholder import MonitorHolder
from windows_holder import WindowsHolder
import time
import logging
import logging.config


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
    log = logging.getLogger(__name__)
    this = Singleton()
    if(this.is_already_running()):
        log.debug("Scriptis already running")
        exit()
    log.warning("Starting Pywinman")
    MonitorHolder()
    WindowsHolder()
else:
    exit()