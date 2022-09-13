r"""This module created a demon thread to listen
a window creation\destruction in windows
"""
import ctypes
import threading
import logging

from win32_wrapper import Win32Wrapper

class WindowMessage:
    def __init__(self, hwnd, title):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.hwnd = hwnd
        self.title = title

    def __repr__(self):
        return f"WinMsg[{self.hwnd}-{self.title}]"

class WindowsHook:
    """ Wrapper for win32 get event loop for getting window in focus """
    def __init__(self, win32):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.w32 = win32

    def register_hook(self, observable, stop_flag):
        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            self.log.debug("WindowsHook callback called")
            length = self.w32.GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            self.w32.GetWindowText(hwnd, buff, length + 1)
            is_minimized = self.w32.IsIconic(hwnd)
            is_active = self.w32.IsWindowVisible(hwnd)
            # Notify observers
            if(length > 0 and (is_active or is_minimized)):
                observable.handle(buff.value, hwnd)
        self.log.debug("WindowsHook callback created")
        hook = self.w32.WinEventHookLoop(callback, stop_flag)
        if hook == 0:
            self.log.error('WinEventHookLoop failed')
            exit(1)

class WindowGetFocusedHandler:
    """ Prints all args when called""" 
    def __init__(self, event_q):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.event_q = event_q

    def handle(self, *args, **kwargs):
        """ Called when a window gets focus """
        self.event_q.put(WindowMessage(args[1], args[0]))
        self.log.debug(args)

class WindowsGetFocusedListener:
    """Creates a win32 listener witch calls listener when triggers"""
    def __init__(self, win32):
        self.w32 = win32
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.__handlers = []
        def run(stop_flag):
            self.log.debug("WindowsGetFocusedListener started")
            hook = WindowsHook(win32)
            hook.register_hook(self, stop_flag)
        self.stop_flag = False
        # Start the 'run' method in a daemonized thread.
        self.d_thread = threading.Thread(target=run, args=(lambda: self.stop_flag,))
        self.d_thread.setDaemon(True)
        self.d_thread.start()

    def stop(self):
        self.log.info("Stopping GetFocused listener")
        self.stop_flag = True
        self.d_thread.join()

    def handle(self, *args, **kwargs):
        """ should be called in win32hook """
        try:
            win_title = str(args[0])
            if win_title == '':
                return ''
            for observer in self.__handlers:
                try:
                    observer.handle(*args)
                except Exception as e:
                    self.log.error("Observer %s failed with %s", observer, e)
        except Exception as e:
            self.log.error("WindowsGetFocusedListener failed during handling %s", e)


    def register_handler(self, handler: WindowGetFocusedHandler):
        """ Registers a hew handler for calling when triggers"""
        self.__handlers.append(handler)

    def __del__(self):
        self.stop()

