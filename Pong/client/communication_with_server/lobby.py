"""
call GUI_Thread.GUI_LobbyClass from here for all gui things
"""

from client import GUI
from server_functions import help_functions


def process_server_msg(msg):
    """
    create reaction to an incoming server message
    """
    pass


def process_command(command):
    """
    :param command: player input
    :return:
    """
    if command == "create_match":
        game = "Pong"
        # i need a list of features that the client and the server ar both able to do and the dims_list
        available_features = ["POWERUPS"]
        dims_list = (800, 600)
        #create_match = GUI.create_or_join()
        #created_match = create_match.gui_create_game(dims_list, available_features)

        feature_selection = created_match[1:None]  # talk about exact format with server guys
        match_name = created_match[0]

        # from create match from tcp_messages
        answer = f"CREATE_MATCH {game} {match_name} {help_functions.pylist2protlist(feature_selection)}"

        byte_server_response = tcp_sock.recv(4096)
        server_response = byte_server_response.decode('ASCII')

    elif command == "":

     return answer, command