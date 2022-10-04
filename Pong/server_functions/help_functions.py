"""a document to store all the small helping functions to use in multiple files"""
from global_settings import STANDARD_ENCODING

def pylist2protlist(pylist: list):
    """a function which transforms a python list into a string list according to the lobby protocol.

    Args:
        pylist: a list that should be transformed into a stringlist divided with "," .
    Returns
        string_list a string which contains the list as a string according to the lobby protocol.
    """
    string_list = ""
    for entry in pylist:  # add each name as a string and a ",".
        string_list += f"{entry},"
    string_list = string_list[:-1]  # delete the last "," as this is not needed
    return string_list


def protlist2pylist(protlist):
    """a function which transforms a string into a pylist according to the lobby protocol.

    Args:
        protlist: a string that should be transformed into a python list.
    Returns
        string_list a string which contains the list as a string according to the lobby protocol.
    """
    pylist = []
    message_array = protlist.split(",")
    for entry in message_array:  # add each name as a string and a ",".
        pylist.append(entry)
    return pylist


def decode_answer(data: bytes, just_one_message=False):
    """
    Args:
        data: (potentially multiple) commands in byte format

    Returns:
    """
    msg = data.decode(STANDARD_ENCODING)
    message_list = msg.split("\0")
    commands = []
    for element in message_list:
        commands.append(element.split(" "))
    if just_one_message:
        commands = commands[0]
    return commands

def split_string_at_nullbyte(message: str):
    message_list = message.split("\0")
    return message_list
