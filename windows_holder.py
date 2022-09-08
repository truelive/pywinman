import ctypes

from ctypes import wintypes


class WindowsHolder:

    def __init__(self):
        self.windows = []
        WindowEnumProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool, 
            wintypes.HWND,
            wintypes.LPARAM)

        def _monitorEnumProc(hWnd, lParam):
            self.windows.append(Window(hWnd))
            return True # continue enumeration

        enum_callback = WindowEnumProc(_monitorEnumProc)
        ctypes.windll.user32.EnumWindows(enum_callback,0)
        # PWINDOWINFO 
        self.windows[0].hwnd
        s = ctypes.create_unicode_buffer(100)
        o = tagWINDOWINFO()
        o.cbSize = ctypes.sizeof(tagWINDOWINFO)
        p = ctypes.byref(o)
        for w in self.windows:
            t = ctypes.windll.user32.GetWindowTextW(w.hwnd, s, 100)
            ctypes.windll.user32.GetWindowInfo(w.hwnd, p)
            print(o, "sad",t) 


class Window:

    def __init__(self, hwnd):
        self.hwnd = hwnd


    def __repr__(self):
        return f"Window[{self.hwnd}]"

class tagWINDOWINFO(ctypes.Structure):
    def __repr__(self):
        return '\n'.join([key + ':' + str(getattr(self, key)) for key, value in self._fields_])

tagWINDOWINFO._fields_ = [
    ('cbSize', wintypes.DWORD),
    ('rcWindow', wintypes.RECT),
    ('rcClient', wintypes.RECT),
    ('dwStyle', wintypes.DWORD),
    ('dwExStyle', wintypes.DWORD),
    ('dwWindowStatus', wintypes.DWORD),
    ('cxWindowBorders',wintypes.UINT),
    ('cyWindowBorders', wintypes.UINT),
    ('atomWindowType', wintypes.ATOM),
    ('wCreatorVersion', wintypes.WORD),
]