import ctypes as ct
from ctypes import wintypes


class Singleinstance:
    """ Limits application to single instance """

    def __init__(self):
        self.mutexname = u"testmutex_{D0E858DF-985E-4907-B7FB-8D732C3FC3B9}"
        self.mutex = ct.windll.kernel32.CreateMutexW(None, ct.c_bool(False), ct.c_wchar_p(self.mutexname))
        print(self.mutex)
        self.lasterror = ct.windll.kernel32.GetLastError()
        print(ct.WinError(self.lasterror))
    
    def alreadyrunning(self):
        return (self.lasterror == 183) #ERROR_ALREADY_EXISTS
        
    def __del__(self):
        if self.mutex:
            ct.windll.kernel32.CloseHandle(self.mutex)