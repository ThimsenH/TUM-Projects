""" The class which handles client requests to the lobby."""

import threading
import socket

from global_settings import STANDARD_ENCODING


class ClientTCPConnectionThread(threading.Thread):
    """ a class for handling the communication with one client.

    The run method ofObjects of this class will be running as a thread parallel to the other code.
    The thread can be started by objectname.start()
    """
    def __init__(self, client_socket: socket.socket, client_address, lobby):
        """

        Args:
            client_socket: the TCP socket with the client
            client_address: the ip address of the client
            lobby: The main lobby. Needed to access data for inter thread communication
        """
        threading.Thread.__init__(self)

        self.c_socket = client_socket
        self.c_address = client_address
        self.lobby = lobby  # this is needed to access data from the lobby object

        print(f"New connection with: {self.c_address} in thread {self.name}")

    def run(self):
        """ method that waits for client messages, processes them and sends back the according answer.

        The while loop of this method runs as a thread.
        The loop should break (and end the thread) once the socket is closed.

        #TODO handle the end of a connection and close thread.
        """
        while True:
            data = self.c_socket.recv(2048)
            msg = data.decode(STANDARD_ENCODING)
            answer = self.process_client_msg(msg)
            self.c_socket.send(bytes(answer, STANDARD_ENCODING))
        self.c_socket.close()

    def process_client_msg(self, msg):
        """ this method gets called by the run method and finds the according answer to the client request.

        Args:
            msg: The decoded message sent received from the client

        Returns:
            answer: A string containing the answer to send to the client
        """
        messageArray = msg.split(" ")
        command = messageArray[0]

        if command == "HELLO":
            # get the list of the clients currently connected with the lobby
            client_list = self.lobby.client_list.get_value()
            answer = f"WELCOME BASIC, Client List: {client_list}"
            messageArray.clear()
            return answer

        if command == "LIST_GAMES":


        if command == "CREATE_MATCH":

        if command == "LIST_MATCHES":

        if command == "MATCH_FEATURES":

        if command == "JOIN_MATCH":

        else:
            return "ERR_CMD_NOT_UNDERSTOOD"
