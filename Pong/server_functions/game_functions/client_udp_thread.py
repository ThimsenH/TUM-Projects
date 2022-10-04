""" The class which handles client udp requests to the lobby."""

import threading
import socket
import collections

import global_settings
# from server_functions.match import MatchClass
from server_functions import help_functions

# imports for autocomplete while coding
from server_functions.client_class import Client


def parsing(msgl):
    string_list = ""
    if len(msgl) > 0:
        message = 0
        message = msgl.popleft()
        for entry in message:
            string_list += f"{entry},"
            string_list = string_list[:-1]
    message_array = string_list.split(" ")
    return message_array


class ClientUDPThread(threading.Thread):

    def __init__(self, match, client_ip, server_port, client: Client):
        threading.Thread.__init__(self)
        self.client = client
        self.match = match
        self.server_port = server_port
        self.client_ip = client_ip  # the IP addr of the client that is supposed to send to this socket
        self.client_port = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # init sock as udp socket
        # self.sock.bind((global_settings.SERVER_IP_ADDR, server_port))
        self.sock.bind(("", server_port))
        self.msgl = collections.deque()

        self.recv_seq_number = global_settings.START_SEQENCE_NUMBER  # the sequence number expected to receive next by the client
        self.send_seq_number = global_settings.START_SEQENCE_NUMBER  # the sequence number which should be send next to the client

    def run(self):
        # wait for the first message from the client in order to get its port
        data, addr = self.sock.recvfrom(1024)
        # if addr[0] == self.client_ip:  # this doesn't really work with localhost
        self.client_port = addr[1]  # store the client port so msg can be send to the client
        msg = data.decode(global_settings.STANDARD_ENCODING)
        self._process_msg(msg, addr)

        self.sock.settimeout(0.1)  # only wait for a new message 0.1 seconds. Send updates minimum every 0.1s

        while self.match.match_running is True:
            try:
                data, addr = self.sock.recvfrom(1024)
                msg = data.decode(global_settings.STANDARD_ENCODING)
                self._process_msg(msg, addr)
            except socket.timeout:
                pass
            except ConnectionResetError:
                pass
            finally:
                self._send_updates()
                if len(self.msgl) != 0:
                    self._process_msg(msg, addr)
        self.sock.close()
        print(f" udp port von {self.client.user_name} geschlossen ")

    def _process_msg(self, msg, addr):
        """tries to read the msg as a KEYS_PRESSED and store the currently pressed keys in the players keys_pressed.

        Returns:
            True: if the reading and storing of the keys_pressed was successful
            False: if not successful (Unknown command or outdated message)
        """
        if msg != 0:
            message_array = msg.split("\0")
            messageArray = 0
            m_list = ""

            for entry in message_array:
                m_list += f"{addr[0]} {addr[1]} {entry}"
                #m_list = m_list[:-1]
                self.msgl.append(m_list)
            msg = 0

        messageArray = parsing(self.msgl)
        if messageArray[0] != self.client_ip:
            return False
        elif len(messageArray) < 4:  # if the len is shorter then two the msg does not match the game_functions protocol
            return False
        elif messageArray[3] != "KEYS_PRESSED":  # if the command is not known
            return False
        elif int(messageArray[2]) < self.recv_seq_number:  # if the msg is not the most current message
            return False
        else:
            # update the expected sequence number to be one bigger then the last received.
            self.recv_seq_number = int(messageArray[2]) + 1

            # store the keys_pressed list thread safe into the players keys_pressed list.
            if len(messageArray) == 4:  # if the keys list is empty
                self.client.keys_pressed.write_value([])  # set the keys pressed list as empty
            else:
                keys_pressed = messageArray[4].split(",")
                self.client.keys_pressed.write_value(keys_pressed)  # set the keys pressed list to new pressed keys
            return True

    def _send_updates(self):
        """reads the position of the ball and both players and send it to the client."""
        # first update the ball position
        ball_position = self.match.ball_position.get_value()
        self._send_msg_ball("UPDATE_BALL", ball_position)

        for client in self.match.client_list:
            player_position = client.position.get_value()
            command = f"UPDATE_PLAYER {client.player_id}"
            self._send_msg_player(command, player_position)

        # TODO: only send this if feature is activated
        if self.match.powerupactivated:
            powerup_positions = self.match.powerup_positions.get_value()
            self._send_msg_powerups("UPDATE_POWERUPS", powerup_positions)

    def _send_msg_ball(self, command: str, value_list: list):
        """transforms the command and value_list into protocol, add seq_number and send the message."""
        obj_no = value_list[0]
        obj_x = value_list[1]
        obj_y = value_list[2]
        obj_x_v = value_list[3]
        obj_y_v = value_list[4]
        msg = f"{self.send_seq_number} {command} {obj_no} {obj_x} {obj_y} {obj_x_v} {obj_y_v}\0"  # TODO add null byte
        self.sock.sendto(msg.encode(global_settings.STANDARD_ENCODING), (self.client_ip, self.client_port))  # TODO This does not work yet
        self.send_seq_number += 1

    def _send_msg_player(self, command: str, value_list: list):
        """transforms the command and value_list into protocol, add seq_number and send the message."""
        obj_x = value_list[0]
        obj_y = value_list[1]
        obj_x_v = value_list[2]
        obj_y_v = value_list[3]
        msg = f"{self.send_seq_number} {command} {obj_x} {obj_y} {obj_x_v} {obj_y_v}\0"   # TODO add null byte
        self.sock.sendto(msg.encode(global_settings.STANDARD_ENCODING),
                         (self.client_ip, self.client_port))  # TODO This does not work yet
        self.send_seq_number += 1

    def _send_msg_powerups(self, command: str, value_list: list):
        """transforms the command and value_list into protocol, add seq_number and send the message."""
        obj1_x = value_list[0]
        obj1_y = value_list[1]
        obj2_x = value_list[2]
        obj2_y = value_list[3]
        msg = f"{self.send_seq_number} {command} {obj1_x} {obj1_y} {obj2_x} {obj2_y}\0"  # TODO add null byte
        self.sock.sendto(msg.encode(global_settings.STANDARD_ENCODING),
                         (self.client_ip, self.client_port))  # TODO This does not work yet
        self.send_seq_number += 1