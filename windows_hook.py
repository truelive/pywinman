r"""This module created a demon thread to listen
a window creation\destruction in windows
"""
import ctypes
import threading
import logging

from win32_wrapper import Win32Wrapper
W32 = Win32Wrapper()

class WindowsHook:
    """ Wrapper for win32 get event loop for getting window in focus """
    def __init__(self):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))

    def register_hook(self, observable, stop_flag):
        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            self.log.debug("WindowsHook callback called")
            length = W32.GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            W32.GetWindowText(hwnd, buff, length + 1)
            is_minimized = W32.IsIconic(hwnd)
            is_active = W32.IsWindowVisible(hwnd)
            # Notify observers
            if(length > 0 and (is_active or is_minimized)):
                observable.handle(buff.value, hwnd)
        self.log.debug("WindowsHook callback created")
        hook = W32.WinEventHookLoop(callback, stop_flag)
        if hook == 0:
            self.log.error('WinEventHookLoop failed')
            exit(1)

class WindowGetFocusedHandler:
    """ Prints all args when called""" 
    def __init__(self):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))

    def handle(self, *args, **kwargs):
        """ Called when a window gets focus """
        self.log.debug(args)

class WindowsGetFocusedListener:
    """Creates a win32 listener witch calls listener when triggers"""
    def __init__(self):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.__handlers = []
        def run(stop_flag):
            self.log.debug("WindowsGetFocusedListener started")
            hook = WindowsHook()
            hook.register_hook(self, stop_flag)
        self.stop_flag = False
        # Start the 'run' method in a daemonized thread.
        self.d_thread = threading.Thread(target=run, args=(lambda: self.stop_flag,))
        self.d_thread.setDaemon(True)
        self.d_thread.start()

    def handle(self, *args, **kwargs):
        """ should be called in win32hook """
        try:
            win_title = ''.join(args[0])
            if win_title == '':
                return ''
            for observer in self.__handlers:
                try:
                    observer.handle(win_title)
                except:
                    self.log.error(observer.__name__, "failed")
        except:
            self.log.error("WindowsGetFocusedListener failed during handling")


    def register_handler(self, handler: WindowGetFocusedHandler):
        """ Registers a hew handler for calling when triggers"""
        self.__handlers.append(handler)

    def __del__(self):
        self.stop_flag = True
