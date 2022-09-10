import ctypes
import logging
from ctypes import wintypes
from win32_wrapper import Win32Wrapper
from windows_hook import WindowsGetFocusedListener, WindowGetFocusedHandler

W32 = Win32Wrapper()

GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
IsIconic = ctypes.windll.user32.IsIconic
GetWindowInfo = ctypes.windll.user32.GetWindowInfo


# Look here for DWORD event constants:
# http://stackoverflow.com/questions/15927262/convert-dword-event-constant-from-wineventproc-to-name-in-c-sharp
# Don't worry, they work for python too.
EVENT_SYSTEM_DIALOGSTART = 0x0010
WINEVENT_OUTOFCONTEXT = 0x0000
EVENT_SYSTEM_FOREGROUND = 0x0003
WINEVENT_SKIPOWNPROCESS = 0x0002

class WindowsHolder:
    def __init__(self):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.windows = []
        # Window GetFocused, also need GetMinimized\Closed\GoesFullScreen
        self.window_listener = WindowsGetFocusedListener()
        self.window_listener.register_handler(WindowGetFocusedHandler())
        def _monitorEnumProc(hWnd, lParam):
            self.windows.append(Window(hWnd))
            return True # continue enumeration
        W32.EnumWindows(_monitorEnumProc)
        W32.PrintWindows(self.windows)
        self.window_listener.d_thread.join()

class Window:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __repr__(self):
        return f"Window[{self.hwnd}]"