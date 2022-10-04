""" Code to run the lobby.

Lobby.run() should be the main thread for the server_functions.
The Lobby starts a thread which listens to the discover lobby broadcasts by clients (DiscoverLobbyAnswerThread).
The Lobby starts a thread for each client that connects via TCP.
"""

import threading
import socket

from server_functions.client_tcp_thread import ClientTCPConnectionThread
from server_functions.lock_object import LockObject
import global_settings
from server_functions.match import MatchClass
from server_functions.client_class import Client


class DiscoverLobbyAnswerThread(threading.Thread):
    """ A class to run a thread which answers the UDP Broadcasts of a client which is searching for a lobby."""

    def __init__(self, lobby_address, lobby_tcp_port):
        """

        Args:
            lobby_address: the ip address where the lobby can be found via TCP
            lobby_tcp_port: the port on which the lobby listens to via TCP
        """
        threading.Thread.__init__(self)
        self.lobby_port = lobby_tcp_port
        self.lobby_address = lobby_address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        self.sock.bind(("", 54000))
        while True:
            data, addr = self.sock.recvfrom(1024)
            msg = data.decode(global_settings.STANDARD_ENCODING)
            message = msg.split("\0")
            if message[0] == "DISCOVER_LOBBY":
                answer = f"LOBBY {global_settings.LOBBY_TCP_PORT}\0"
                print(answer)
                self.sock.sendto(answer.encode(global_settings.STANDARD_ENCODING), addr)


class LobbyClass:
    """ A class to host the lobby.

    The object holds all the inter thread data for the hole lobby.
    Usually just one object of this should be created.
    The run method of this object should be the main thread of the hole script.
    """

    HOST_IP_ADDR = global_settings.SERVER_IP_ADDR
    lobby_tcp_port = global_settings.LOBBY_TCP_PORT

    def __init__(self):
        print("Creating Lobby")
        self.client_list = LockObject([])
        self.match_dict = LockObject({})
        self.lowest_free_udp_port = LockObject(global_settings.GAME_UDP_PORTS_START)
        #self.lowest_free_player_id = 0
        # TODO:  gamefeatures festlegen
        self.game_features = LockObject(["BASIC", "POWERUPS"])

    def run(self):
        # start broadcast listening thread to help clients discover this lobby
        discover_lobby_thread = DiscoverLobbyAnswerThread(self.HOST_IP_ADDR, self.lobby_tcp_port)
        discover_lobby_thread.start()

        # create a TCP server_functions to listen for new client connections via TCP
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.HOST_IP_ADDR, self.lobby_tcp_port))
        print("Lobby server_functions started")
        print("Waiting for client request..")

        # listen for new client connections to the lobby
        while True:
            server.listen(1)
            client_sock, client_address = server.accept()
            new_client = Client(client_address)  # create a new client object for this client
            # create a tcp connection thread for this client and start it
            new_client.tcp = ClientTCPConnectionThread(client_sock, client_address, self, new_client)
            new_client.tcp.start()

            # store the ip address of a new client in the client list.
            # do this without any other thread being able to access the value while it's changed.
            self.client_list.lock.acquire()
            self.client_list.value.append(new_client)
            self.client_list.lock.release()

    def create_match(self, game: str, match_name: str, game_features: list):
        """
        Args:
            game: The Game for which a match should be created. E.g. Pong
            match_name: The name of the match
            game_features: The features which the match should support
        """
        if game != "Pong":  # if the requested game is not supported by this server
            answer = f"ERR_FAILED_TO_CREATE in this lobby only Pong is available. Your requested Game was {Game}"

        elif match_name in self.match_dict.get_value().keys():
            answer = f"ERR_FAILED_TO_CREATE you chose {match_name} as the name of the match, but {match_name} already exists"

        # überprüft, ob alle angefragten game_features auch vom server unterstützt werden
        elif len(set(self.game_features.get_value()).intersection(game_features)) != len(game_features):
            answer = f"ERR_FAILED_TO_CREATE you chose {game_features} as gamefeatures, but this lobby only supports {self.game_features.get_value()}"
        else:
            match_udp_ports = self._get_free_udp_ports(2)  # TODO make this according to the number of clients
            self.match_dict.lock.acquire()
            self.match_dict.value[match_name] = MatchClass(match_name, game_features, match_udp_ports)
            self.match_dict.lock.release()
            for cli in self.client_list.get_value():
                cli.interupt_case=4
            answer = "MATCH_CREATED"
        return answer

    def _get_free_udp_ports(self, amount: int):
        udp_ports = []
        for i in range(amount):
            self.lowest_free_udp_port.lock.acquire()
            udp_ports.append(self.lowest_free_udp_port.value)
            self.lowest_free_udp_port.value += 1
            self.lowest_free_udp_port.lock.release()
        return udp_ports

    #def get_free_player_id(self):
    #    player_id = self.lowest_free_player_id
    #    self.lowest_free_player_id += 1
    #   return player_id
