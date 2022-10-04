""" A class to store values thread safe with threading.Lock()"""

import threading


class LockObject:
    """ a class for easily creating an object which can be locked. """

    def __init__(self, value):
        self.value = value
        self.lock = threading.Lock()

    def get_value(self, blocking=True, timeout=-1):
        """read the value thread safe.

        Args:
            blocking: When invoked with the blocking argument set to True (the default),
                        block until the lock is unlocked, then set it to locked and return True.
                      When invoked with the blocking argument set to False, do not block.
                        If a call with blocking set to True would block, return False immediately;
                        otherwise, set the lock to locked and return True.
            timeout: When invoked with the floating-point timeout argument set to a positive value,
                        block for at most the number of seconds specified by timeout and as long as the lock cannot
                        be acquired. A timeout argument of -1 specifies an unbounded wait.
                        It is forbidden to specify a timeout when blocking is false.

        returns:
            data: the value stored in self.value
            False: if the value could not be read threadsafe
        """
        if self.lock.acquire(blocking, timeout) is True:
            data = self.value
            self.lock.release()
            return data
        else:
            return False

    def write_value(self, data, blocking=True, timeout=-1):
        """write the value thread safe.

        Args:
            data: the data to write in self.value
            blocking: the blocking argument to pass to lock.acquire
            timeout: the timeout argument to pass to lock.aquire
        """
        if self.lock.acquire(blocking, timeout) is True:
            self.value = data
            self.lock.release()
            return True
        else:
            return False
