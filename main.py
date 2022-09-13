""" Pywinman starter"""
import signal
import logging
import logging.config
import queue
from EventQueue import EventQueue
from singleton import Singleton
from monitorsholder import MonitorHolder
from windows_holder import WindowsHolder
from windows_hook import WindowMessage
from hotkey_listener import HotkeyListener
from hotkey_listener import HotkeyMessage
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
    evns = EventQueue(queue.SimpleQueue())
    MonitorHolder()
    w_holder = WindowsHolder(Win32Wrapper(), evns)
    holder = HotkeyListener(Win32Wrapper(), evns)
    holder.stop_flag
    stop_flag = False
    def signal_handler(sig, frame):
        LOG.warning("EXIT IS CALLED")
        global stop_flag
        stop_flag = True
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    print('Press Ctrl+C')
    # EventQueue listener
    while not stop_flag:
        res = evns.get()
        if res is not None:
            if isinstance(res, WindowMessage):
                LOG.debug(res)
                w_holder.handle_msg(res)
                pass
            if isinstance(res, HotkeyMessage):
                # action
                pass
    LOG.info("Closing Pywinman")
    holder.stop()
    LOG.info("hotkey holder stopped")
    w_holder.stop()
    LOG.info("window holder stopped")
else:
    exit()
