"""
handle all errors with this class
"""


class ERROR(Exception):
    """
    ERROR class methods shall be called if an error message has to be sent.
    The error message is sent within the ERROR class method so its just 1 line
    """

    def send(self, return_message):
        print(return_message)
        connection.sendall(return_message)

    def ERR_CMD_NOT_UNDERSTOOD(self, reason):
        return_message = "ERR_CMD_NOT_UNDERSTOOD"
        return_message += " " + reason
        self.send(return_message)

    def ERR_FAILED_TO_CREATE(self, reason):
        return_message = "ERR_FAILED_TO_CREATE "
        return_message += " " + reason
        self.send(return_message)

    def ERR_FAILED_TO_JOIN(self, reason):
        return_message = "ERR_FAILED_TO_JOIN "
        return_message += " " + reason
        self.send(return_message)

    def ERR_GAME_NOT_EXIST(self, name):
        return_message = "ERR_GAME_NOT_EXIST "
        return_message += " " + name
        self.send(return_message)

    def DISCONNECTING_YOU(self, reason):
        return_message = "DISCONNECTING_YOU"
        return_message += " " + reason
        self.send(return_message)


class ERR_FAILED_TO_JOIN(ERROR):
    def __init__(self, reason):
        return_message = "ERR_FAILED_TO_JOIN "
        return_message += " " + reason
        self.send(return_message)
