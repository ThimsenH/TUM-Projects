""" The class which handles client requests to the lobby."""

import threading
import socket
import collections

from global_settings import STANDARD_ENCODING
from server_functions import help_functions
from server_functions.help_functions import pylist2protlist
from server_functions.match import MatchClass


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

class ClientTCPConnectionThread(threading.Thread):
    """ a class for handling the communication with one client.

    The run method ofObjects of this class will be running as a thread parallel to the other code.
    The thread can be started by objectname.start()
    """

    def __init__(self, client_socket: socket.socket, client_address, lobby, client_object):
        """

        Args:
            client_socket: the TCP socket with the client
            client_address: the ip address of the client
            lobby: The main lobby. Needed to access data for inter thread communication
            client: The client object of which this TCP socket is part.
        """
        threading.Thread.__init__(self)

        self.client = client_object
        self.c_socket = client_socket
        self.c_address = client_address
        self.lobby = lobby  # this is needed to access data from the lobby object
        self.game_start = False
        self.msgl = collections.deque()

        print(f"New connection with: {self.c_address} in thread {self.name}")

    def run(self):
        """ method that waits for client messages, processes them and sends back the according answer.

        The while loop of this method runs as a thread.
        The loop should break (and end the thread) once the socket is closed.

        #TODO handle the end of a connection and close thread.
        """
        self.c_socket.settimeout(0.1)
        while True:
            try:
                data = self.c_socket.recv(2048)
                msg = data.decode(STANDARD_ENCODING)
                answer = self.process_client_msg(msg) + "\0"
                if answer is not "Stop\0":
                    self.c_socket.send(bytes(answer, STANDARD_ENCODING))
                while len(self.msgl) > 0:
                    answer = self.process_client_msg(msg) + "\0"
                    if answer is not "Stop\0": #wird nur gebraucht, falls der Client I_AM_READY schickt, da der server dann nicht antwortet
                        self.c_socket.send(bytes(answer, STANDARD_ENCODING))
            except socket.timeout:  # 0.1 Seknude sind abgelaufen, überprüfen, ob client etwas senden muss
                if self.client.interupt_case == 0: # es passiert nichts, der Client muss keine Nachrichtn senden
                    pass
                elif self.client.interupt_case == 1: #client bekommt Nachricht, dass Partie beginnt, weil noch ein anderer Cleint in sein match gejoint is
                    answer = f"MATCH_STARTED {self.client.udp.server_port} {self.client.match.client_list[0].player_id},{help_functions.pylist2protlist(self.client.match.client_list[0].color)},{self.client.match.client_list[1].player_id},{help_functions.pylist2protlist(self.client.match.client_list[1].color)}\0"
                    print(f'sending "{answer}" to {self.client.user_name}')
                    self.c_socket.send(bytes(answer, STANDARD_ENCODING))
                    self.client.interupt_case = 0
                elif self.client.interupt_case == 2: #SCORE_UPDATE das Spieler 1 (=players[0]) in Gameclass einen neuen Score hat
                    answer = f"SCORE_UPDATE {self.client.match.client_list[0].player_id} {self.client.match._logic.player1Score}\0"
                    # print(answer)
                    print(f'sending "{answer}" to {self.client.user_name}')
                    self.c_socket.send(bytes(answer, STANDARD_ENCODING))
                    self.client.interupt_case = 0
                elif self.client.interupt_case == 3: #SCORE_UPDATE das Spieler 2 (=players[1]) in Gameclass einen neuen Score hat
                    answer = f"SCORE_UPDATE {self.client.match.client_list[1].player_id} {self.client.match._logic.player2Score}\0"
                    # print(answer)
                    print(f'sending "{answer}" to {self.client.user_name}')
                    self.c_socket.send(bytes(answer, STANDARD_ENCODING))
                    self.client.interupt_case = 0
                elif self.client.interupt_case == 4:  # updaten der matchliste falls ein neues Match dazugekommen ist
                    self.lobby.match_dict.lock.acquire()
                    match_list_as_string = help_functions.pylist2protlist(self.lobby.match_dict.value)
                    self.lobby.match_dict.lock.release()
                    answer = "GAMES Pong " + match_list_as_string
                    #self.c_socket.send(bytes(answer, STANDARD_ENCODING))
                    self.client.interupt_case = 0
                elif self.client.interupt_case == 5: #ein anderer Spieler hat dein aktuelles game verlassen du gewinnst:
                    answer = f"GAME_ENDED you won, because the other player left the game!\0"
                    print(f'sending "{answer}" to {self.client.user_name}')
                    self.c_socket.send(bytes(answer, STANDARD_ENCODING))
                    self.client.interupt_case = 0
                elif self.client.interupt_case == 6: #client won
                    answer = f"GAME_ENDED you won, because you reached the max gamescore!\0"
                    print(f'sending "{answer}" to {self.client.user_name}')
                    self.c_socket.send(bytes(answer, STANDARD_ENCODING))
                    self.client.interupt_case = 0
                elif self.client.interupt_case == 7: #client loose
                    answer = f"GAME_ENDED you lost, because your opponent reached the max gamescore!\0"
                    print(f'sending "{answer}" to {self.client.user_name}')
                    self.c_socket.send(bytes(answer, STANDARD_ENCODING))
                    self.client.interupt_case = 0
                elif self.client.interupt_case == 8: #client loose
                    answer = f"GAME_ENDED you lost, because you left the game!\0"
                    print(f'sending "{answer}" to {self.client.user_name}')
                    self.c_socket.send(bytes(answer, STANDARD_ENCODING))
                    self.client.interupt_case = 0
                elif self.client.interupt_case == 4:  #updaten der matchliste falls ein neues Match dazugekommen ist
                    self.lobby.match_dict.lock.acquire()
                    match_list_as_string = help_functions.pylist2protlist(self.lobby.match_dict.value)
                    self.lobby.match_dict.lock.release()
                    answer = "GAMES Pong testetstetstets " + match_list_as_string
                    self.c_socket.send(bytes(answer, STANDARD_ENCODING))
                    self.client.interupt_case = 0
                    #except self.game_logic.score_update == True:
               #answer = f"SCORE_UPDATE {self.client.player_id} {self.game.score}"
               #self.c_socket.send(bytes(answer, STANDARD_ENCODING))
               #self.game_logic.score_update = False
               #break

            # except self.game_logic.score_update == True:
            #    answer = f"SCORE_UPDATE {self.client.player_id} {self.game.score}"
            #    self.c_socket.send(bytes(answer, STANDARD_ENCODING))
            #    self.game_logic.score_update = False
            #    break
            except ConnectionResetError:
                # TODO: wenn Client TCP socket schließt.
                print(f'{self.client.user_name} disconected case 1')
                #self.lobby.client_list.lock.acquire()
                #del self.lobby.client_list.value[]
                #self.lobby.client_list.lock.release()
                if self.client.match is not None: #falls er eh in keinem match ist, gibt es auch kein problem
                    if self.client.match.match_running: # game beendet, es gibt einen gewinner
                        self.client.match.match_running = False
                        self.client.match.ball_moving = False
                        print(f'{self.client.match.name} ended, because {self.client.user_name} disconected ')
                        for cli in self.client.match.client_list:  # informieren der anderen Clients über TCP, die davor gejoint sind,
                            if cli != self:
                                cli.interupt_case=5
                    else: # Match is not running -> man ist eh alleine im game -> man entfernt sich aus dem game indem man die Liste leert
                        self.client.match.client_list = []
                        print(f'{self.client.user_name} left game "{self.client.match.name}", because {self.client.user_name} disconected ')
                break

            except ConnectionAbortedError:
                print(f'{self.client.user_name} disconected case 2')
                if self.client.match is not None: #falls er eh in keinem match ist, gibt es auch kein problem
                    if self.client.match.match_running: # game beendet, es gibt einen gewinner
                        self.client.match.match_running = False
                        self.client.match.ball_moving = False
                        print(f'{self.client.match.name} ended, because {self.client.user_name} disconected ')
                        for cli in self.client.match.client_list:  # informieren der anderen Clients über TCP, die davor gejoint sind,
                            if cli != self:
                                cli.interupt_case=5
                    else: # Match is not running -> man ist eh alleine im game -> man entfernt sich aus dem game indem man die Liste leert
                        self.client.match.client_list = []
                        print(f'{self.client.user_name} left game "{self.client.match.name}", because {self.client.user_name} disconected ')
                break

        self.c_socket.close()

    def process_client_msg(self, msg):
        """ this method gets called by the run method and finds the according answer to the client request.

        Args:
            msg: The decoded message sent received from the client

        Returns:
            answer: A string containing the answer to send to the client
        """

        command=''
        message_array = msg.split("\0")
        messageArray = 0
        del (message_array[len(message_array) - 1])

        for entry in message_array:
            self.msgl.append(entry)

        while len(self.msgl) > 0:
            messageArray = parsing(self.msgl)
            command = messageArray[0]

        # TODO: Ich (Roman) fände es gut, wenn hier von jedem if statement eine eigene Funktion aufgerufen werden würde.
        if command != '':
            if command == "HELLO":
                self.client.user_name = messageArray[1]
                # TODO [list<CLIENT_FEATURES>]=messageArray[2] verarbeiten

                # get the list of the clients currently connected with the lobby
                feature_list = self.lobby.game_features.get_value()
                feature_list = help_functions.pylist2protlist(feature_list)
                answer = f"WELCOME BASIC,DIMS,80,60,10,10,{feature_list}"  # TODO DIMS List
                messageArray.clear()
                return answer

            elif command == "LIST_GAMES":
                # Request a list of available games
                answer = "AVAILABLE_GAMES Pong"
                return answer
            elif command == "CREATE_MATCH":

                Game = messageArray[1]
                match_name = messageArray[2]

                # get requested game features and transform them into a python list
                if len(messageArray) >= 4:
                    list_game_features = messageArray[3].split(",")
                    if list_game_features == ['']:
                        list_game_features = ['BASIC']
                    if list_game_features == ['POWERUPS']:
                        list_game_features = ['POWERUPS']
                else:
                    list_game_features = ['BASIC']

                answer = self.lobby.create_match(Game, match_name, list_game_features)

                return answer

            elif command == "LIST_MATCHES":
                Game = messageArray[1]
                if Game == "Pong":
                    self.lobby.match_dict.lock.acquire()
                    match_list_as_string = help_functions.pylist2protlist(self.lobby.match_dict.value)
                    self.lobby.match_dict.lock.release()
                    if len(self.lobby.match_dict.value)>0:
                        answer = "GAMES Pong " + match_list_as_string
                        print(f"sending answer typ 1{answer}")
                    else:
                        answer = "GAMES Pong"
                        print(f"sending answer typ 2{answer}")
                else:
                    answer = f"ERR_GAME_NOT_EXIST " + Game
                print(answer)
                return answer

            elif command == "MATCH_FEATURES":
                match = messageArray[1]
                #features_list_as_string = help_functions.pylist2protlist(self.match.gamefeatures_dict.value)
                if match in self.lobby.match_dict.value:
                    features_list_as_string = self.lobby.match_dict.value[match].gamefeatures
                    if features_list_as_string == "BASIC":
                        answer = "MATCH Pong " + match
                    else:
                        answer = "MATCH Pong " + match + " " + pylist2protlist(features_list_as_string)
                else:
                    answer = "ERR_MATCH_NOT_EXIST"
                return answer

            elif command == "JOIN_MATCH":
                # ungefähr so :
                match_name = messageArray[1]
                color = messageArray[2].split(',')  # messageArray[2]
                print(messageArray[2])
                print(f"color from {self.client.user_name} empfangen von {color}")
                if match_name in self.lobby.match_dict.get_value().keys():  # versuchen dem match zu joinen
                    self.lobby.match_dict.lock.acquire()
                    answer_from_match = self.lobby.match_dict.value[match_name].join_match(self.client)
                    self.lobby.match_dict.lock.release()
                    if answer_from_match == "FALL1":
                        self.client.match = self.lobby.match_dict.value[match_name]
                        self.client.player_id = self.client.match.get_player_id(self.client)

                        self.client.color = color
                        print(f'{self.client.user_name} joined match {self.client.match.name} with color {color}')

                        answer = f"MATCH_JOINED {self.client.player_id}"
                    elif answer_from_match == "FALL2":
                        answer = f"ERR_FAILED_TO_JOIN match ist schon voll"
                    elif answer_from_match == "FALL3":
                        self.client.match = self.lobby.match_dict.value[match_name]
                        self.client.player_id = self.client.match.get_player_id(self.client)

                        self.lobby.match_dict.lock.acquire()
                        del self.lobby.match_dict.value[match_name]
                        self.lobby.match_dict.lock.release()

                        self.client.color = color
                        print(f'{self.client.user_name} joined match {self.client.match.name} with color {color}')

                        answer1 = f"MATCH_JOINED {self.client.player_id}\0"
                        self.c_socket.send(bytes(answer1, STANDARD_ENCODING))

                        answer = f"MATCH_STARTED {self.client.udp.server_port} {self.client.match.client_list[0].player_id},{help_functions.pylist2protlist(self.client.match.client_list[0].color)},{self.client.match.client_list[1].player_id},{help_functions.pylist2protlist(self.client.match.client_list[1].color)}"
                        print(f'sending "{answer}" to {self.client.user_name}')
                    else:
                        answer = f"ERR_FAILED_TO_JOIN Server hat Fehler"
                else:
                    answer = f"ERR_FAILED_TO_JOIN There is no joinable match named {match_name}"
                return answer

            elif command == "LEAVING_MATCH":
                reason = messageArray[1]
                print(f'{self.client.user_name} leaving match, because "{reason}"')
                #del self.client.match.clientlist[self.client.user_name]
                #resulting_client = self.client.match.clientlist.pop()
                #del self.lobby.match_dict[self.client.match.name]
                self.client.match.match_running = False
                self.client.match.ball_moving = False
                self.client.interupt_case = 8
                for cli in self.client.match.client_list:  # informieren der anderen Clients über TCP, die davor gejoint sind,
                    if cli != self:
                        cli.interupt_case = 5

                return

            elif command == "I_AM_READY":
                self.client.i_am_ready = True
                self.client.match.i_am_ready(self.client)
                return "STOP"

            else:
                return "ERR_CMD_NOT_UNDERSTOOD"


    #def end_match(self, winner):
     #   answer = f"GAME_ENDED {winner} won!"
      #  #
       # del self.lobby.match_dict[self.match_name]
        #return answer

    # Disconnecting Client if Game calls Function
    #def disconnecting_client(self, reason):
     #   answer = f"DISCONNECTING_YOU {reason}"
      #  self.c_socket.send(bytes(answer, STANDARD_ENCODING))
       # self.c_socket.close()
        #return
