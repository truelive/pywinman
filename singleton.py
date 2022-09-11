""" Used to check if created more than one instance of the program """
import logging
import ctypes as ct

class Singleton:
    """ Checks if an application is already started """
    def __init__(self):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.mutex_name = u"test_mutex_{D0E858DF-985E-4907-B7FB-8D732C3FC3B9}"
        self.mutex = ct.windll.kernel32.CreateMutexW(
            None,
            ct.c_bool(False),
            ct.c_wchar_p(self.mutex_name)
        )
        self.last_error = ct.windll.kernel32.GetLastError()

    def is_already_running(self):
        """ Checks for last known error during the creation """
        return self.last_error == 183 #ERROR_ALREADY_EXISTS

    def __del__(self):
        if self.mutex:
            ct.windll.kernel32.CloseHandle(self.mutex)
