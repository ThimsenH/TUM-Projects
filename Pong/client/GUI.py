# install requests, Pillow
from tkinter import *
from tkinter import font as tkFont
import tkinter as tk
from client.communication_with_server.tcp_messages import TCPConnection


class name_player():

    def name_selection(self, dims_list, error_space,error_name):
        # init, will be realized as seperate function in the future
        # screen,backroundimage
        self.error_space = error_space
        self.error_name = error_name
        self.dims_list = dims_list
        self.root = tk.Tk()
        self.root.title("Pong Game Group 4")
        self.canvas = tk.Canvas(self.root, height=dims_list[1], width=dims_list[0])
        self.canvas.pack()
        self.helv15 = tkFont.Font(family='Helvetica', size=15, weight='bold')
        self.backround_image = tk.PhotoImage(file="client/Backround.png")
        self.pong_image = tk.PhotoImage(file="client/Pong_im.png")
        self.backround_label = tk.Label(self.root, image=self.backround_image)
        self.backround_label.place(x=0, y=0, relwidth=1, relheight=1)
        # name entry
        self.frame_game_name = tk.Frame(self.root)
        self.frame_game_name.place(anchor="n", relx=0.5, rely=0.25, relwidth=0.35, relheight=0.25)
        self.label = tk.Label(self.frame_game_name, image=self.pong_image, bg="black")
        self.label.place(relwidth=1, relheight=1)
        self.frame = tk.Frame(self.root, bg="black", bd=5)
        self.frame.place(anchor="n", relx=0.5, rely=0.7, relwidth=0.6, relheight=0.1)
        # name confirmation button
        self.enter_name_button = tk.Button(self.frame, font=self.helv15, text="Select Name", bg="gray", fg="black",
                                           command=lambda: self.get_name())
        self.enter_name_button.place(relx=0.66, relheight=1, relwidth=0.34)
        self.entry_name = tk.Entry(self.frame, font=self.helv15)
        self.entry_name.place(relheight=1, relwidth=0.65)
        if self.error_space:
            self.error_frame = tk.Frame(self.root)
            self.error_frame.place(anchor="n", relx=0.5, rely=0.6, relwidth=0.5, relheight=0.05)
            self.error_label = tk.Label(self.error_frame, text="ERROR: Name mustn't contain Space", bg="gray",font=self.helv15)
            self.error_label.place(relheight=1, relwidth=1)
            self.error_space=False
        if self.error_name:
            self.error_frame = tk.Frame(self.root)
            self.error_frame.place(anchor="n", relx=0.5, rely=0.6, relwidth=0.3, relheight=0.05)
            self.error_label = tk.Label(self.error_frame, text="ERROR: Enter Name first", bg="gray",font=self.helv15)
            self.error_label.place(relheight=1, relwidth=1)
            self.error_name = False
        self.root.mainloop()
        return self.player_name

    def get_name(self):
        self.error_space = False
        self.player_name = self.entry_name.get()
        self.name_list = self.player_name.split(" ")
        if len(self.name_list)!=1:
            self.error_space = True
            self.root.destroy()
            self.name_selection(self.dims_list,self.error_space,self.error_name)
        elif not self.player_name:
            self.error_name = True
            self.root.destroy()
            self.name_selection(self.dims_list, self.error_space,self.error_name)
        else:
            self.root.destroy()


class create_or_join():
    def __init__(self, tcp, game):
        self.tcp = tcp
        self.game = game

    def create_or_join_game(self, dims_list, joinable_matches):
        joinable_matches = joinable_matches
        # init, will be realized as seperate function in the future
        # screen,backroundimage
        self.root = tk.Tk()
        self.root.title("Pong Game Group 4")
        self.canvas = tk.Canvas(self.root, height=dims_list[1], width=dims_list[0])
        self.canvas.pack()
        self.backround_image = tk.PhotoImage(file="client/Backround.png")
        self.backround_label = tk.Label(self.root, image=self.backround_image)
        self.backround_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame_game_name = tk.Frame(self.root)
        self.frame_game_name.place(anchor="n", relx=0.5, rely=0.05, relwidth=0.3, relheight=0.15)
        self.pong_image = tk.PhotoImage(file="client/Pong_im.png")
        self.label = tk.Label(self.frame_game_name, image=self.pong_image, bg="black")
        self.label.place(relwidth=1, relheight=1)
        # style and size of font
        self.helv13 = tkFont.Font(family='Helvetica', size=13, weight='bold')
        self.helv17 = tkFont.Font(family='Helvetica', size=17, weight='bold')
        # frame and list with available games
        self.frame_game = tk.Frame(self.root)
        self.frame_game.place(anchor="n", relx=0.5, rely=0.25, relheight=0.05, relwidth=0.6)
        self.label_game = tk.Label(self.frame_game, text="Available Matches", font=self.helv17, fg="black", bg="#636363")
        self.label_game.place( relwidth=1, relheight=1)
        self.frame = tk.Frame(self.root)
        self.frame.place(anchor="n", relx=0.5, rely=0.3, relheight=0.5, relwidth=0.6)
        # scrollbar
        self.scrollbar = tk.Scrollbar(self.frame, orient=VERTICAL)
        # puts available games into listbox
        self.games_list = tk.Listbox(self.frame, yscrollcommand=self.scrollbar.set, fg="black", bg="#908080",
                                     font=self.helv17, selectbackground="#474545")
        self.games_list.pack(side="left", fill="both", expand=True)
        for match in joinable_matches:
            self.games_list.insert(0, match)
        # buttons
        self.select_button = tk.Button(self.root, text="Join Game", font=self.helv13, bg="#908080",
                                       command=lambda: self.join_game())
        self.select_button.place(relx=0.3, rely=0.85, relheight=0.08, relwidth=0.15)
        self.create_button = tk.Button(self.root, text="Create Game", font=self.helv13, bg="#908080",
                                       command=lambda: self.create_game())
        self.create_button.place(relx=0.55, rely=0.85, relheight=0.08, relwidth=0.15)
        self.update_button = tk.Button(self.root, text="Update Games", font=self.helv13, bg="black",fg="white",
                                       command=lambda: self.update_matches())
        self.update_button.place(relx=0.82, rely=0.5, relheight=0.1, relwidth=0.15)

        self.scrollbar.config(command=self.games_list.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.root.mainloop()
        return self.answer

    def update_matches(self):
        self.games_list.destroy()
        self.games_list = tk.Listbox(self.frame, yscrollcommand=self.scrollbar.set, fg="black", bg="#908080",
                                     font=self.helv17, selectbackground="#474545")
        self.games_list.pack(side="left", fill="both", expand=True)
        joinable_matches = self.tcp.list_matches(self.game)
        for match in joinable_matches:
            self.games_list.insert(0, match)


    def join_game(self):
        self.name_joined_game = self.games_list.get(ANCHOR)
        print(self.name_joined_game)
        if len(self.name_joined_game)!=0:
         self.select_button.destroy()
         self.create_button.destroy()
         self.games_list.destroy()
         self.helv17 = tkFont.Font(family='Helvetica', size=17, weight='bold')
         self.color_list = tk.Listbox(self.frame,  fg="black", bg="#908080",
                                     font=self.helv17, selectbackground="#474545")
         self.color_list.pack(side="left", fill="both", expand=True)
         self.color_button = tk.Button(self.root, text="Select Color", font=self.helv13, bg="#908080",
                                      command=lambda: self.choose_color())
         self.color_button.place(relx=0.4, rely=0.85, relheight=0.08, relwidth=0.2)
         self.available_colors = ["WHITE","RED", "GREEN", "BLUE","YELLOW", "PINK"]
         for color in self.available_colors:
            self.color_list.insert(END, color)
        else:
            self.name_joined_game = self.games_list.get(ANCHOR)

    def choose_color(self):
        self.color_chosen = self.color_list.get(ANCHOR)
        if len(self.color_chosen)!=0:
         if self.color_chosen == "WHITE":
            rgb_color= (255,255,255)
         elif self.color_chosen == "RED":
            rgb_color= (255,0,0)
         elif self.color_chosen == "GREEN":
            rgb_color= (0,255,0)
         elif self.color_chosen == "BLUE":
            rgb_color= (0,0,255)
         elif self.color_chosen == "YELLOW":
            rgb_color= (255,255,0)
         elif self.color_chosen == "PINK":
            rgb_color= (255,20,147)
         else:
            rgb_color=(255,255,255)
         self.root.destroy()
         self.answer = ["join_match", self.name_joined_game, rgb_color]

         return self.answer
        else:
            self.color_chosen = self.color_list.get(ANCHOR)

    def create_game(self):
        self.root.destroy()
        self.answer = ["create_match"]
        return self.answer

    def gui_create_game(self, dims_list, available_features,error_name,error_space):
        # init, will be realized as seperate function in the future
        # screen,backroundimage
        self.dims_list = dims_list
        self.available_features = available_features
        self.root = tk.Tk()
        self.root.title("Pong Game Group 4")
        self.canvas = tk.Canvas(self.root, height=dims_list[1], width=dims_list[0])
        self.canvas.pack()
        self.backround_image = tk.PhotoImage(file="client/Backround.png")
        self.backround_label = tk.Label(self.root, image=self.backround_image)
        self.backround_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.helv15 = tkFont.Font(family='Helvetica', size=15, weight='bold')
        # Logo
        self.frame_game_name = tk.Frame(self.root)
        self.frame_game_name.place(anchor="n", relx=0.5, rely=0.05, relwidth=0.3, relheight=0.15)
        self.pong_image = tk.PhotoImage(file="client/Pong_im.png")
        self.label = tk.Label(self.frame_game_name, image=self.pong_image, bg="black")
        self.label.place(relwidth=1, relheight=1)
        # frame for name with button
        self.frame = tk.Frame(self.root, bg="black", bd=5)
        self.frame.place(anchor="n", relx=0.5, rely=0.8, relwidth=0.6, relheight=0.1)
        self.helv13 = tkFont.Font(family='Helvetica', size=13, weight='bold')
        self.enter_name_button = tk.Button(self.frame, font=self.helv13, text="Select Game Name", bg="gray", fg="black",
                                           command=lambda: self.created_game())
        # name entry and button to confirm entry
        self.enter_name_button.place(relx=0.66, relheight=1, relwidth=0.34)
        self.entry_game_name = tk.Entry(self.frame, font=self.helv15)
        self.entry_game_name.place(relheight=1, relwidth=0.65)
        # frame for features
        self.frame_list_features = tk.Frame(self.root)
        self.frame_list_features.place(anchor="n", relx=0.5, rely=0.25, relwidth=0.6, relheight=0.4)
        self.var = StringVar()
        self.features_list = tk.Listbox(self.frame_list_features, fg="black", bg="#908080",
                                        font=self.helv15, selectbackground="#474545", selectmode=MULTIPLE)
        self.features_list.pack(side="left", fill="both", expand=True)
        for feature in available_features:
            self.features_list.insert(END, feature)

        if error_space:
            self.error_frame = tk.Frame(self.root)
            self.error_frame.place(anchor="n", relx=0.5, rely=0.7, relwidth=0.5, relheight=0.05)
            self.error_label = tk.Label(self.error_frame, text="ERROR: Name mustn't contain Space", bg="gray",
                                            font=self.helv15)
            self.error_label.place(relheight=1, relwidth=1)

        elif error_name:
            self.error_frame = tk.Frame(self.root)
            self.error_frame.place(anchor="n", relx=0.5, rely=0.7, relwidth=0.5, relheight=0.05)
            self.error_label = tk.Label(self.error_frame, text="ERROR: Enter Game Name", bg="gray",
                                            font=self.helv15)
            self.error_label.place(relheight=1, relwidth=1)
        self.root.mainloop()
        return self.created_game

    def created_game(self):
        self.chosen_game_name = self.entry_game_name.get()
        self.clicked_features = self.features_list.curselection()
        self.chosen_features = []
        for feature in self.clicked_features:
            self.chosen_features.append(self.features_list.get(feature))
        self.name_list = self.chosen_game_name.split(" ")

        if len(self.name_list) != 1:
            self.root.destroy()
            self.gui_create_game(self.dims_list,self.available_features, False, True)

        elif not self.chosen_game_name:
            self.root.destroy()
            self.gui_create_game(self.dims_list, self.available_features, True, False)
        else:
            self.root.destroy()
            self.name_game = [self.chosen_game_name]
            self.created_game = self.name_game + self.chosen_features




