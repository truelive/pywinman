import ctypes
from ctypes import wintypes

# Callback Factory
class MonitorHolder:
    def __init__(self):
        self.monitors = []
        MonitorEnumProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool, 
            wintypes.HMONITOR,
            wintypes.HDC,
            wintypes.LPRECT,
            wintypes.LPARAM)

        def _monitorEnumProc(hMonitor, hdcMonitor, lprcMonitor, dwData):
            self.monitors.append(Monitor(hMonitor, hdcMonitor, lprcMonitor, dwData))
            print('call result:', hMonitor, hdcMonitor, lprcMonitor, dwData)
            return True # continue enumeration

        # Make the callback function
        enum_callback = MonitorEnumProc(_monitorEnumProc)

        def enum_mons():   
            '''Enumerate the display monitors.'''
            return ctypes.windll.user32.EnumDisplayMonitors(
                None, 
                None,
                enum_callback,
                0)
        enum_mons()
        print(self.monitors)

class Monitor:
    def __init__(self, hMonitor, hdcMonitor, lprcMonitor, dwData):
        self.hMonitor = hMonitor
        self.hdcMonitor = hdcMonitor
        r = lprcMonitor[0]
        self.rect = (r.top, r.left, r.bottom, r.right) # resolution lprcMonitor[0].right, lprcMonitor[0].bottom
    
    def __repr__(self):
        return f"Monitor[{self.rect}]{self.hMonitor}"