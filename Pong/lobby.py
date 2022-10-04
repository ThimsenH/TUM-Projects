""" Code to run the lobby.

Lobby.run() should be the main thread for the server.
The Lobby starts a thread which listens to the discover lobby broadcasts by clients (DiscoverLobbyAnswerThread).
The Lobby starts a thread for each client that connects via TCP.
"""

import threading
import socket

from client_tcp_thread import ClientTCPConnectionThread
from lock_object import LockObject
import global_settings


class DiscoverLobbyAnswerThread(threading.Thread):
    """ A class to run a thread which answers the UDP Broadcasts of a client which is searching for a lobby."""
    def __init__(self, lobby_address, lobby_tcp_port):
        """

        Args:
            lobby_address: the ip address where the lobby can be found via TCP
            lobby_tcp_port: the port on which the lobby listens to via TCP
        """
        threading.Thread.__init__(self)
        # TODO: Create an UDP socket which listens to the Broadcast on port 54000
        self.lobby_port = lobby_tcp_port
        self.lobby_address = lobby_address
        pass

    def run(self):
        # TODO Answer with the TCP Lobby port
        pass

class LobbyClass:
    """ A class to host the lobby.

    The object holds all the inter thread data for the hole lobby.
    Usually just one object of this should be created.
    The run method of this object should be the main thread of the hole script.
    """

    LOCALHOST = global_settings.LOCALHOST
    lobby_tcp_port = global_settings.LOBBY_TCP_PORT

    def __init__(self):
        print("Creating Lobby")
        self.client_list = LockObject([])

    def run(self):
        # start broadcast listening thread to help clients discover this lobby
        discover_lobby_thread = DiscoverLobbyAnswerThread(self.LOCALHOST, self.lobby_tcp_port)
        discover_lobby_thread.start()

        # create a TCP server to listen for new client connections via TCP
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.LOCALHOST, self.lobby_tcp_port))
        print("Lobby server started")
        print("Waiting for client request..")

        # listen for new client connections to the lobby
        while True:
            server.listen(1)
            client_sock, client_address = server.accept()

            # store the ip address of a new client in the client list.
            # do this without any other thread being able to access the value while it's changed.
            self.client_list.lock.acquire()
            self.client_list.value.append(client_address)
            self.client_list.lock.release()

            # run a thread for every client that connects via TCP
            tcp_client_thread = ClientTCPConnectionThread(client_sock, client_address, self)
            tcp_client_thread.start()

