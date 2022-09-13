import logging
import threading

class HotkeyMessage:
    def __init__(self, mod, key):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.key = key
        self.mod = mod

    def __repr__(self):
        return f"Hotkey[{self.mod}+{self.key}]"


class HotkeyListener:
    def __init__(self, win32, event_q):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.w32 = win32
        def run(stop_flag, event_q):
            self.log.debug("WindowsGetFocusedListener started")
            win32.RegisterHotKey()
            hook = HotkeyHook(win32, event_q)
            hook.register_hook(stop_flag)
            win32.UnregisterHotKey()
        self.stop_flag = False
        # Start the 'run' method in a daemonized thread.
        self.d_thread = threading.Thread(target=run, args=(lambda: self.stop_flag, event_q))
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
    def __init__(self, win32, event_q):
        self.w32 = win32
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.event_q = event_q

    def put(self, *args):
        self.event_q.put(HotkeyMessage(args[0], args[1]))

    def register_hook(self, stop_flag):
        self.log.debug("WindowsHook callback created")
        hook = self.w32.WinListenKeysHookLoop(stop_flag, self)
        if hook != 0:
            self.log.error('WinEventHookLoop failed')
