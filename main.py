""" Pywinman starter"""
import sys
import signal
import logging
import logging.config
import time
from singleton import Singleton
from monitorsholder import MonitorHolder
from windows_holder import WindowsHolder
from hotkey_listener import HotkeyListener
from win32_wrapper import Win32Wrapper



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
    w_holder = WindowsHolder(Win32Wrapper())
    holder = HotkeyListener(Win32Wrapper())
    def signal_handler(sig, frame):
        LOG.info("Closing Pywinman")
        holder.stop()
        LOG.info("hotkey holder stopped")
        w_holder.stop()
        LOG.info("window holder stopped")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    print('Press Ctrl+C')
    # EventQueue listener
    time.sleep(30)
    holder.stop()
    w_holder.stop()
else:
    exit()
