""" The class wich defines matches
"""

import threading
# import socket
import pygame

# from client_tcp_thread import ClientTCPConnectionThread
from server_functions.lock_object import LockObject
import global_settings
from server_functions.game_functions.game_logic import Logic
from server_functions.game_functions.client_udp_thread import ClientUDPThread
from server_functions.client_class import Client


class MatchClass(threading.Thread):
    """ A class to safe the diffrent matches, wich are created by the clients.

    The object holds all the data for one match.
    One object of this should be created for every match.
    """

    LOCALHOST = global_settings.LOCALHOST
    lobby_tcp_port = global_settings.LOBBY_TCP_PORT

    def __init__(self, match_name, gamefeatures: list, udp_ports: list):
        """
            Args:
                match_name: the name of the match. set by CREATE_MATCH-TCPcommand from Client
                gamefeatures: list with gamefeatures which, the match should have. set by CREATE_MATCH-TCPcommand from Client
                udp_ports: a list of the udp_ports that should be used for game communication.
        """
        threading.Thread.__init__(self)
        print(f"Creating new Match {match_name}")
        self.name = match_name
        self.gamefeatures = gamefeatures
        print(self.gamefeatures)
        self.client_list = []
        #self.score = []

        self.udp_ports = udp_ports

        # values for the game
        self.max_players = 2  # the maximum amount of players allowed in one game. This should be set dynamicly

        self.ball_position = LockObject([0, 0, 0, 0, 0])  # ball_number, x, y, x_v, y_v
        self.score = LockObject([0, 0])  # [score_p1, score_p2]
        self._logic = Logic(self)
        self._clock = pygame.time.Clock()

        self.match_running = False
        self.ball_moving = False

        self.powerup_positions = LockObject([0, 0, 0, 0])  # Box 1 x, y; Box 2 x, y
        if self.gamefeatures == ['POWERUPS']:
            self.powerupactivated = True
            print("Powerups active in this match")
        else:
            self.powerupactivated = False
            print("Powerups not active in this match")

    def run(self):  # is this needed?
        """The game_functions threads main function.

                This function can be stared as a thread by Game.start()
                """
        self.match_running = True
        while self.match_running:
            # update logic with new inputs. The logic gets the keys pressed directly from the player objects
            self._logic.update_player_positions()

            # calculate the current game state
            if self.ball_moving:
                self._logic.update_state()
                if self._logic.score_update1 or self._logic.score_update2:
                    if self._logic.score_update1:
                        for client in self.client_list:
                            client.interupt_case = 2
                        self._logic.score_update1 = False
                    if self._logic.score_update2:
                        for client in self.client_list:
                            client.interupt_case = 3
                        self._logic.score_update2 = False
                if self._logic.player1won or self._logic.player2won:
                    if self._logic.player1won:
                        self.client_list[0].interupt_case = 6
                        self.client_list[1].interupt_case = 7
                        self._logic.player1won = False
                        self.ball_moving = False
                        self.match_running = False
                    if self._logic.player2won:
                        self.client_list[0].interupt_case = 7
                        self.client_list[1].interupt_case = 6
                        self._logic.player2won = False
                        self.ball_moving = False
                        self.match_running = False  # set this to False so the game calculating while loop ends

            # Update PowerUp Boxes
            if self.powerupactivated:
                self._logic.update_box1()
                self._logic.update_box2()
                self._logic.get_powerup_state()

            # write the just calculated positions in the Lock Objects so they can be send by the udp threads.
            self._logic.write_positions()

            if self.powerupactivated:
                self._logic.write_powerup_positions()

            # update loop 60 times per second
            self._clock.tick(60)

        for cli in self.client_list:
            cli.match = None
            print(f"bei {cli.user_name} wurde matchatribute =None gesetzt")

    def start_game(self):
        """start the game logic and both udp threads. send match_started msg via TCP."""
        self.start()
        self.match_running = True  # this has to be done before starting the UDP Threads. They only run if this is True.
        self._start_udp_threads()


    def _start_udp_threads(self):
        for i, client in enumerate(self.client_list):
            udp_port = self.udp_ports[i]
            udp_thread = ClientUDPThread(self, client.ip_addr[0], udp_port, client)
            client.udp = udp_thread
            client.udp.start()

    def join_match(self, new_client: Client):
        """
            -fügt einen Client hinzu, vorrausgesetzt das MAtch ist nicht schon voll
            -wenn 2 Cleints drin sind: starte game_functions:
                            ruft in ClientTCPConnectionThread Funktion auf die MATCH_STARTED schickt)
                            startet von gamethread/ udp verbindungen

        :return:

        #
        """

        if len(self.client_list) < global_settings.MAX_SPIELER_PRO_MATCH:
            self.client_list.append(new_client)
            print(f'{new_client.user_name} joined game {self.name}')

            if len(self.client_list) == global_settings.MAX_SPIELER_PRO_MATCH:
                # Match wird gestartet:
                answer = "FALL3"  # Fall 3: gejoint und match startet
                self.start_game()
                for cli in self.client_list:  # informieren der anderen Clients über TCP, die davor gejoint sind,
                    if cli != new_client:  # client_list(0)
                        cli.interupt_case = 1  # Funktioniert so vllt, da muss ich mir noch was überlegen

            else:
                answer = "FALL1"  # wird im clientthread, der diese Funktion aufgerufen hat, also der als letztes gejoint ist, benutz um zu erkenn ob das Game gleich startet oder nicht: FAll1: client match gejoint

        else:
            answer = "FALL2"  # FAll2: client match nicht gejoint, weil schon voll

        return answer

    def i_am_ready(self, client: Client):
        client.i_am_ready = True
        game_kann_starten = True
        for cl in self.client_list:
            if not cl.i_am_ready:
                game_kann_starten = False
        self.ball_moving = game_kann_starten
        print(f"Ball running in game{self.name}")

    def get_player_id(self, client):
        return self.client_list.index(client)+1


