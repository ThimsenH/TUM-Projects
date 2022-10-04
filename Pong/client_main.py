import socket
from client.communication_with_server.UDP_broadcast import server_discovery
from client import GUI
from client import  game_gui_thread
from client.communication_with_server.tcp_messages import TCPConnection
from client.communication_with_server.tcp_messages import tcp_during_game
import global_settings
from server_functions import help_functions
from multiprocessing import Process
import tkinter as tk
from tkinter import font as tkFont


class Match:
    """an object that should hold all the important data for a match."""
    def __init__(self):
        self.game_type = None
        self.features = None
        self.name = None
        # data for a player
        self.player_id = None
        self.player_color = None
        self.opp_color = (255,255,255)

class Lobby:
    def __init__(self):
        self.tcp = None
        self.udp_dst = None
        self.server_ip = None
        self.server_port = None
        self.game = None
        self.dims = []
        self.func_dims = []
        self.available_features = ["BASIC","POWERUPS"]
        self.server_supported_features = []
        self.both_supported_features = []
        self.match = Match()
        self.created_match = []
        self.player_name = None
        self.tcp_during_game = None
        self.waiting_thread= Process(target= self.waiting_thread_func)

    def waiting_thread_func(self):

        self.root1 = tk.Tk()
        self.canvas = tk.Canvas(self.root1, height=600, width=800)
        self.canvas.pack()
        self.helv30 = tkFont.Font(family='Helvetica', size=30, weight='bold')
        self.backround_image = tk.PhotoImage(file="client/Backround.png")
        self.backround_label = tk.Label(self.root1, image=self.backround_image)
        self.backround_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.waiting_frame = tk.Frame(self.root1)
        self.waiting_frame.place(anchor="n", relx=0.5, rely=0.3, relwidth=0.5, relheight=0.4)
        self.waiting_label = tk.Label(self.waiting_frame, text="Waiting for \n Opponent to join", font=self.helv30,
                                      bg="gray")
        self.waiting_label.place(relheight=1, relwidth=1)
        self.root1.mainloop()



    def setup_lobby(self):
        # self.server_ip = global_settings.SERVER_IP_ADDR
        # self.server_port = global_settings.LOBBY_TCP_PORT
        self.server_ip, self.server_port = server_discovery()
        self.tcp = TCPConnection(self.server_ip, self.server_port, self)
        while not self.player_name:
          self._name_choosing()

        # send hello message with our feature
        self._send_hello_msg()

    def _name_choosing(self):
        name_class = GUI.name_player()

        while self.player_name == None:
         self.player_name = name_class.name_selection((800,600),False,False)

    def _send_hello_msg(self):
        self.tcp.send_hello(self.player_name)

    def match_overview_2_joined_match(self):
        """Step through the lobby indefinitely."""
        self.func_dims = [int(self.dims[0]) * int(self.dims[2]), int(self.dims[1]) * int(self.dims[3])]
        while True:
            # first get the list of joinable matches
            joinable_matches = self.tcp.list_matches(self.game)
            # display these matches in the GUI so the player can either create a game or join a game
            self.create_or_join = GUI.create_or_join(self.tcp,self.game)
            user_choice = self.create_or_join.create_or_join_game(self.func_dims, joinable_matches)

            if user_choice[0] == "create_match":
                self._create_match()  # True if match was created successfully, False else

            elif user_choice[0] == "join_match":
                # self.waiting_thread.start()
                self.match.name = user_choice[1]
                self.match.player_color = user_choice[2]
                # join the match
                joined_match_successful = self.tcp.join_match(self.match)
                if joined_match_successful is True:
                    # match joined successfully
                    # wait until match starts TODO display an according message to the user
                    match_started_successful = self._handle_match_start()
                    return match_started_successful

    def run_match(self):
        game_objects = game_gui_thread.GameObjects()

        udp_connection = game_gui_thread.UDPCommunicationThread(self.udp_dst, game_objects)
        udp_connection.start()
        self.tcp_during_game = tcp_during_game(self.tcp.sock)
        self.tcp_during_game.start()
        game_gui = game_gui_thread.GameGUI(self.func_dims, game_objects,self, self.match.player_color, self.match.opp_color)
        game_gui.run() # !WARNUNG: hier verharren wir auf unbestimmte Zeit, bis das Spiel beendet ist!

    def _create_match(self):
        """ask user for match specification and send the requested specs to the server"""
        # display a gui in which the user can create a match

        while not self.created_match:
          self.created_match = self.create_or_join.gui_create_game(self.func_dims, self.both_supported_features,False,False)

        match_name = self.created_match[0]
        selected_features = self.created_match[1:None]  # talk about exact format with server guys

        # set self.created_match back to None so we enter the while loop when we want to create another game
        self.created_match = None
        # send a tcp request to the server to create a game
        return self.tcp.create_match(self.game, match_name, selected_features)

    def _handle_match_start(self):
        #self.gui_thread = GUI.gui_thread()
        #self.gui_thread.start()
        data = self.tcp.sock.recv(global_settings.BUFF_SIZE)
        answer = help_functions.decode_answer(data, just_one_message=True)
        if answer[0] == "MATCH_STARTED":
            # self.waiting_thread.terminate()
            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_dst = (self.server_ip, int(answer[1]))

            # resolve player colors
            player_color_list = help_functions.protlist2pylist(answer[2])
            if player_color_list[0] == "1":
                self.match.player_color = (int(player_color_list[1]),int(player_color_list[2]),int(player_color_list[3]))
                self.match.opp_color = (int(player_color_list[5]),int(player_color_list[6]),int(player_color_list[7]))
            else:
                self.match.player_color = (int(player_color_list[5]),int(player_color_list[6]),int(player_color_list[7]))
                self.match.opp_color = (int(player_color_list[1]),int(player_color_list[2]),int(player_color_list[3]))
            return True
        else:
            return False


if __name__ == "__main__":
    lobby = Lobby()
    lobby.game = "Pong"



    while True:

        lobby.setup_lobby()

        match_joined = lobby.match_overview_2_joined_match()

        if match_joined is True:
            lobby.run_match()
            match_joined = False
