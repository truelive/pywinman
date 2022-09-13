import ctypes
from ctypes import wintypes
import logging

class Win32Wrapper:
    def __init__(self):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.GetWindowText = ctypes.windll.user32.GetWindowTextW
        self.GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        self.IsWindowVisible = ctypes.windll.user32.IsWindowVisible
        self.IsIconic = ctypes.windll.user32.IsIconic
        self.GetWindowInfo = ctypes.windll.user32.GetWindowInfo
        self.GetLastError = ctypes.windll.kernel32.GetLastError 
        self.SetLastError = ctypes.windll.kernel32.SetLastError 
        self.TranslateMessageW = ctypes.windll.user32.TranslateMessage

        # Look here for DWORD event constants
        # http://stackoverflow.com/questions/15927262/convert-dword-event-constant-from-wineventproc-to-name-in-c-sharp
        self.EVENT_SYSTEM_DIALOGSTART = 0x0010
        self.EVENT_SYSTEM_FOREGROUND = 0x0003
        self.WINEVENT_OUTOFCONTEXT = 0x0000
        self.WINEVENT_SKIPOWNPROCESS = 0x0002
        self.WM_HOTKEY = 0x0312
        self.WT_TIMER = 0x0113

    def RegisterHotKey(self, mod=0x01, key=0x4F):
        res = ctypes.windll.user32.RegisterHotKey(None, 133, mod | 0x4000, key) # 0x42 -'b' 0x08 - WINKEY
        if res == 0:
            self.log.error("RegisterHotKey %s ", ctypes.WinError(self.GetLastError()))

    def UnregisterHotKey(self):
        res = ctypes.windll.user32.RegisterHotKey(None, 133) # 0x42 -'b' 0x08 - WINKEY
        if res == 0:
            self.log.error("RegisterHotKey %s ", ctypes.WinError(self.GetLastError()))

    def WinListenKeysHookLoop(self, stop_flag, event_q):
        timer = ctypes.windll.user32.SetTimer(None, None, 1000, None)
        ctypes.windll.ole32.CoInitialize(0)
        msg = ctypes.wintypes.MSG()
        self.log.debug("calling GetMessageW  first")
        res = ctypes.windll.user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)
        self.log.debug("Entering GetMessageW loop")
        while not stop_flag() and res != 0:
            if msg.message == self.WM_HOTKEY:
                event_q.put(msg.message, 0)
                self.log.debug("WM_HOTKEY %s", msg.message)
                self.TranslateMessageW(msg)
                ctypes.windll.user32.DispatchMessageW(msg)
            res = ctypes.windll.user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)
        ctypes.windll.ole32.CoUninitialize()
        ctypes.windll.user32.KillTimer(None, timer)
        self.log.warning('Stopped receiving new hotkey events. Exiting...')
        return 0

    def WinEventHookLoop(self, callback, stop_flag):
        """ Creates a win32 hook that calls for a call back when gets triggered.
        Should be called in separate thread
        """
        timer = ctypes.windll.user32.SetTimer(None, None, 1000, None)
        ctypes.windll.ole32.CoInitialize(0)
        self.log.debug("ole32 init")
        win_event_fun_factory = ctypes.WINFUNCTYPE(
            None,
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.HWND,
            wintypes.LONG,
            wintypes.LONG,
            wintypes.DWORD,
            wintypes.DWORD
        )
        self.log.debug("Win32 callback factory init")
        # check for callback format ?
        win32_callback = win_event_fun_factory(callback)
        self.log.debug("Win32 callback create")
        ctypes.windll.user32.SetWinEventHook.restype = wintypes.HANDLE
        hook = ctypes.windll.user32.SetWinEventHook(
            self.EVENT_SYSTEM_FOREGROUND,
            self.EVENT_SYSTEM_FOREGROUND,
            0,
            win32_callback,
            0,
            0,
            self.WINEVENT_OUTOFCONTEXT | self.WINEVENT_SKIPOWNPROCESS
        )
        self.log.debug("SetWinEventHook called ")
        if hook == 0:
            self.log.error("SetWinEventHook failed to execute")
            return hook
        msg = ctypes.wintypes.MSG()
        self.log.debug("calling GetMessageW  first")
        res = ctypes.windll.user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)
        self.log.debug("Entering GetMessageW loop")
        while not stop_flag() and res != 0:
            if(msg.message != self.WT_TIMER):
                self.TranslateMessageW(msg)
                ctypes.windll.user32.DispatchMessageW(msg)
            res = ctypes.windll.user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)

        self.log.warning('Stopped receiving new window change events. Exiting...')
        ctypes.windll.user32.UnhookWinEvent(hook)
        ctypes.windll.user32.KillTimer(None, timer)
        ctypes.windll.ole32.CoUninitialize()
        return hook

    def EnumWindows(self, callback):
        WindowEnumProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool, 
            wintypes.HWND,
            wintypes.LPARAM)
        enum_callback = WindowEnumProc(callback)
        ctypes.windll.user32.EnumWindows(enum_callback, 0)

    def PrintWindows(self, windows):
        o = tagWINDOWINFO()
        o.cbSize = ctypes.sizeof(tagWINDOWINFO)
        p = ctypes.byref(o)
        for w in windows:
            self.SetLastError(0)
            length = self.GetWindowTextLength(w)
            err = self.GetLastError()
            if(err != 0):
                self.log.error("GetWindowTextLength " + ctypes.WinError(err))
            s = ctypes.create_unicode_buffer(length+1)
            res = self.GetWindowText(w, s, length+1)
            if res == 0:
                 err = self.GetLastError()
                 if(err != 0):
                    self.log.error("GetWindowText " + ctypes.WinError(err))
            res = self.GetWindowInfo(w, p)
            if res == 0:
                 err = self.GetLastError()
                 self.log.error("GetWindowInfo" + ctypes.WinError(err))
            is_minimized = self.IsIconic(w)
            is_active = self.IsWindowVisible(w)
            if(length > 0 and (is_minimized or is_active)):
                self.log.debug("%s %s -- %s", o.dwStyle, o.rcWindow.bottom, s.value) 
                # TODO store filtered windows
        
class tagWINDOWINFO(ctypes.Structure):
    _fields_ = [
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

    def __repr__(self):
        return '\n'.join([key + ':' + str(getattr(self, key)) for key, value in self._fields_])
