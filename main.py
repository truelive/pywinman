from ctypes import wintypes
import ctypes as ct
from singleton import Singleinstance
from monitorsholder import MonitorHolder
from windows_holder import WindowsHolder
import time

if __name__ == "__main__":
    this = Singleinstance()
    if(this.alreadyrunning()):
        print("Scriptis already running")
        exit()
    MonitorHolder()
    WindowsHolder()
else:
    exit()