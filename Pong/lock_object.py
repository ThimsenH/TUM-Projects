""" A class to store values thread safe with threading.Lock()"""

import threading


class LockObject:
    """ a class for easily creating an object which can be locked. """
    def __init__(self, value):
        self.value = value
        self.lock = threading.Lock()

    def get_value(self):
        """read the value thread safe."""
        self.lock.acquire()  # TODO add blocking and timeout arguments
        data = self.value
        self.lock.release()
        return data
