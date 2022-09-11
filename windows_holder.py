import ctypes
import logging
from ctypes import wintypes
from win32_wrapper import Win32Wrapper
from windows_hook import WindowsGetFocusedListener, WindowGetFocusedHandler

# Look here for DWORD event constants:
# http://stackoverflow.com/questions/15927262/convert-dword-event-constant-from-wineventproc-to-name-in-c-sharp
# Don't worry, they work for python too.
EVENT_SYSTEM_DIALOGSTART = 0x0010
WINEVENT_OUTOFCONTEXT = 0x0000
EVENT_SYSTEM_FOREGROUND = 0x0003
WINEVENT_SKIPOWNPROCESS = 0x0002

class WindowsHolder:
    def __init__(self, win32):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.windows = []
        # Window GetFocused, also need GetMinimized\Closed\GoesFullScreen
        self.window_listener = WindowsGetFocusedListener()
        self.window_listener.register_handler(WindowGetFocusedHandler())
        def _monitorEnumProc(hWnd, lParam):
            self.windows.append(Window(hWnd))
            return True # continue enumeration
        win32.EnumWindows(_monitorEnumProc)
        win32.PrintWindows(self.windows)
    
    def stop(self):
        self.log.info("Stopping Windows holder")
        self.window_listener.stop()

class Window:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __repr__(self):
        return f"Window[{self.hwnd}]"