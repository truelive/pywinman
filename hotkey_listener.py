import logging
import threading

class HotkeyListener:
    def __init__(self, win32):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.w32 = win32
        def run(stop_flag):
            self.log.debug("WindowsGetFocusedListener started")
            win32.RegisterHotKey()
            hook = HotkeyHook(win32)
            hook.register_hook(stop_flag)
            win32.UnregisterHotKey()
        self.stop_flag = False
        # Start the 'run' method in a daemonized thread.
        self.d_thread = threading.Thread(target=run, args=(lambda: self.stop_flag,))
        self.d_thread.setDaemon(True)
        self.d_thread.start()
    
    def stop(self):
        self.log.debug("Stopping")
        self.stop_flag = True
        self.d_thread.join()

    def __del__(self):
        self.stop()

class HotkeyHook:
    """ Wrapper for win32 get event loop for getting window in focus """
    def __init__(self, win32):
        self.w32 = win32
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))

    def register_hook(self, stop_flag):
        self.log.debug("WindowsHook callback created")
        hook = self.w32.WinListenKeysHookLoop(stop_flag)
        if hook != 0:
            self.log.error('WinEventHookLoop failed')