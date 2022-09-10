import ctypes as ct
from ctypes import wintypes
import logging

class Singleton:
    """ Limits application to single instance """
    def __init__(self):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.mutexname = u"testmutex_{D0E858DF-985E-4907-B7FB-8D732C3FC3B9}"
        self.mutex = ct.windll.kernel32.CreateMutexW(None, ct.c_bool(False), ct.c_wchar_p(self.mutexname))
        self.log.debug(self.mutex)
        self.last_error = ct.windll.kernel32.GetLastError()
        self.log.debug(ct.WinError(self.last_error))
    
    def is_already_running(self):
        return (self.last_error == 183) #ERROR_ALREADY_EXISTS
        
    def __del__(self):
        if self.mutex:
            ct.windll.kernel32.CloseHandle(self.mutex)