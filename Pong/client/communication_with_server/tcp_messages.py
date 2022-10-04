"""
client
"""
import socket
import threading
import collections
from server_functions.lock_object import LockObject
from server_functions import help_functions
from client.communication_with_server import tcp_messages as tcp
# from client.GUI_Thread import GUI_Render
import global_settings
from server_functions import help_functions as hf


class TCPConnection:
    def __init__(self, server_ip, server_tcp_port, lobby):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server_ip, server_tcp_port))
        self.lobby = lobby

    def send_hello(self, player_name):
        """Send HELLO msg to server and return server_features and dims."""
        # send the hello message to the server
        client_features = help_functions.pylist2protlist(self.lobby.available_features)
        message = f"HELLO {player_name} {client_features}\0"
        self.sock.sendall(message.encode(global_settings.STANDARD_ENCODING))

        # receive the WELCOME MESSAGE from the server
        data = self.sock.recv(global_settings.BUFF_SIZE)
        command_list = hf.decode_answer(data, just_one_message=True)

        if command_list[0] == "WELCOME":
            server_config = hf.protlist2pylist(command_list[1])
            for index, item in enumerate(server_config):
                if item == "DIMS":
                    # cut off the DIMS info and put only the
                    # feature info in server_features
                    self.lobby.server_supported_features = server_config[index+5:]
                    self.lobby.server_supported_features.append('BASIC')
                    self.lobby.both_supported_features = []

                    for i in range(len(self.lobby.available_features)):
                        print(self.lobby.available_features[i])
                        if self.lobby.available_features[i] in self.lobby.server_supported_features:
                            self.lobby.both_supported_features.append(self.lobby.available_features[i])

                    # cut off the feature info and put only
                    # the DIMS numbers in the list DIMS
                    dims = server_config[(index + 1):]
                    dims = dims[:4]
                    dims_as_int = []
                    for dim in dims:
                        dims_as_int.append(int(dim))
                    self.lobby.dims = dims_as_int
            print(f"hello() returning server features: {self.lobby.server_supported_features}, "
                  f"and DIMS: {self.lobby.dims}")
            return True
        else:
            print(f"ERR_CMD_NOT_UNDERSTOOD, server msg: {answer}")
            self.sock.sendall("ERR_CMD_NOT_UNDERSTOOD".encode(global_settings.STANDARD_ENCODING))
            return False

    def list_matches(self, game):
        """
            ask the server for a list of all joinable matches of a game category.
            :param game: (str) game category (i.e. "Pong")

        """
        list_of_matches = []
        msg = f"LIST_MATCHES {game}\0"
        self.sock.sendall(msg.encode(global_settings.STANDARD_ENCODING))
        list_of_playable_matches = []
        data = self.sock.recv(global_settings.BUFF_SIZE)
        answer = hf.decode_answer(data, just_one_message=True)
        print(f"both_supported_features: {self.lobby.both_supported_features}")
        #if self.lobby.both_supported_features

        if answer[1] == game and len(answer) > 2:
            list_of_matches = hf.protlist2pylist(answer[2])
            for i in range(len(list_of_matches)):
                if list_of_matches[i] != "":
                    feature = self.match_features(list_of_matches[i])
                    if "5" in feature: #nur damit wir auch mit Gruppe 5 spielen können
                        feature = ["BASIC"]
                    if len(set(self.lobby.both_supported_features).intersection(feature)) == len(feature):
                        list_of_playable_matches.append(list_of_matches[i])
            print(f"list_of_playable_matches: {list_of_playable_matches}")
            return list_of_playable_matches
        else:
            return list_of_playable_matches

    def match_features(self, match_name):
        msg = f"MATCH_FEATURES {match_name}\0"
        self.sock.sendall(msg.encode(global_settings.STANDARD_ENCODING))

        data = self.sock.recv(global_settings.BUFF_SIZE)
        answer = hf.decode_answer(data, just_one_message=True)
        print(f"antwort auf MATCH_FEATURES: {answer}")
        return answer[3].split(",")

    def create_match(self, game, match_name, selected_features):
        """
        ask server to create a new match
        :param game: (str) game category (i.e. "Pong")
        :param match_name: name the user gave the match
        :param selected_features: features the user wants the match to have
        :return None
        """
        message = f"CREATE_MATCH {game} {match_name} {hf.pylist2protlist(selected_features)}\0"
        self.sock.sendall(message.encode(global_settings.STANDARD_ENCODING))

        data = self.sock.recv(global_settings.BUFF_SIZE)
        answer = hf.decode_answer(data, just_one_message=True)

        if answer[0] == "MATCH_CREATED":
            print(f"created match {match_name}")
            return True
        else:
            print(f"failed to create match. ERROR: {answer}")
            return False

    def join_match(self, match):
        """
        join an available match
        :param match_name: (str) match the player wants to join
        :param player_color: (str) color the player has
        :return: if success:    player_id (str) used to match UPDATE_PLAYER msg to me or opponent
        """
        message = f"JOIN_MATCH {match.name} {help_functions.pylist2protlist(match.player_color)}\0"
        self.sock.sendall(message.encode(global_settings.STANDARD_ENCODING))

        data = self.sock.recv(global_settings.BUFF_SIZE)
        answer = hf.decode_answer(data, just_one_message=True)

        if answer[0] == "MATCH_JOINED":
            match.player_id = answer[1]
            return True
        elif answer[0] == "ERR_FAILED_TO_JOIN":
            print(f"failed to join match {match.name} because of {answer[1]}")
            return False

    def send_i_am_ready(self):
        msg = "I_AM_READY\0"
        self.sock.sendall(msg.encode(global_settings.STANDARD_ENCODING))


class tcp_during_game(threading.Thread):
    """ A class for communicating with the server during the game. """

    def __init__(self, tcp_sock):
        """
        Args:
            tcp_sock: socket for sending and receiving messages from/to server

        if the user quits the game the game gui should write the corresponding message (without nullbyte)
        in the variable self.from_user_messages using the code:
        self has to be replaced with the instance of the thread
        ____________________________________________________________________________________
        self.from_user_messages.lock.acquire()
        self.from_user_messages.value.append("string the server can understand without nullbyte")
        self.from_user_messages.lock.release()
        ____________________________________________________________________________________

        messages from the server can be looked up in the self.from_server_messages like that:
        ____________________________________________________________________________________
        self.from_server_messages.lock.acquire()
            try:
                # set server_message to the oldest enty in the message list:
                server_message = self.from_server_messages.value.popleft()
            except IndexError:
                # no message in from_user_messages
                pass
            finally:
                self.from_server_messages.lock.release()
        ____________________________________________________________________________________
        now if there is a server message you have it in the variable server_message.
        You can react if there is no server message in the except IndexError section.
        """
        threading.Thread.__init__(self)

        self.tcp_sock = tcp_sock

        self.from_server_messages = LockObject([]) #todo richtig verwendet??
        self.from_user_messages = LockObject([])

        # make both variables to a queue to make them able to hold more than 1 message
        self.from_user_messages.lock.acquire() # todo kann ich das schon oben in der iniialisierung vom LockObject machen?
        self.from_user_messages.value = collections.deque()
        self.from_user_messages.lock.release()
        self.from_server_messages.lock.acquire()
        self.from_server_messages.value = collections.deque()
        self.from_server_messages.lock.release()

    def run(self):
        self.tcp_sock.settimeout(1)
        while True:

            # look if there is a message from user to server
            # if so, user_message holds the value of the message, else pass
            self.from_user_messages.lock.acquire()
            try:
                # set user_message to the oldest enty in the message list and add nullbyte:
                user_message = f"{self.from_user_messages.value.popleft()}\0"
                # todo maybe process user_message
                # send user_message to server (only executed if there is no IndexError):
                self.tcp_sock.send(user_message.encode(global_settings.STANDARD_ENCODING))
            except IndexError:
                # no message in from_user_messages
                pass
            finally:
                self.from_user_messages.lock.release()

            # wait for a server message to arrive, if no message for 0.1sec -> timeout -> pass
            # if a message is arriving -> write it in the self.from_server_messages variable
            try:
                data = self.tcp_sock.recv(global_settings.BUFF_SIZE)
                server_message_list = hf.decode_answer(data)
                # print(server_message_list)
                self.from_server_messages.lock.acquire()
                # put all the single messages received from server in the list in self.from_server_messages.value
                for element in server_message_list:
                    self.from_server_messages.value.append(element)
                self.from_server_messages.lock.release()
            except socket.timeout:
                pass
            except ConnectionResetError:
                break
            except ConnectionAbortedError:
                break

        self.tcp_sock.close()

