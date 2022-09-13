import queue
import logging

class EventQueue:
    def __init__(self, queue_impl):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.q = queue_impl

    def get(self, timeout=1):
        try:
            res = self.q.get(block=True, timeout=timeout)
        except queue.Empty:
            self.log.debug("None mes in the queue returning None")
            res = None
        return res

    def put(self, obj):
        self.q.put(obj)
