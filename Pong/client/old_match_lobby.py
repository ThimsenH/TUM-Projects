

def match_lobby(tcp_sock, server_ip, game, dims_list, command):

    joinable_matches = tcp.list_matches(tcp_sock, game)

    # todo: (gui) display joinable matches of game and ask if user wants to join and existing match
    #  or to create a new one
    create_or_join = GUI.create_or_join()
    command = GUI.create_or_join.create_or_join_game(create_or_join, (800, 800), joinable_matches)
    # for joining a match we need 2 outputs from gui here
    # 1. info that we want to join a match (like "join_match")
    # 2. name of the match we want to join
    # I assume its 1 string with the 2 infos split with " "

    # the 2 possible command formats:
    # test_color = "117,112,179"
    # command = "create_match"
    # command = "join_match name_of_a_joinable_match" + " " + test_color

    # Marco: right now I am sending a list, so we don`t get a problem if the game name contains a space key

    if command[0] == "create_match":

        # todo: (gui) ask user for match_name and features the features he wants the match to have
        # i need a list of features that the client and the server ar both able to do and the dims_list
        available_features = ["feature1", "feature2"]
        dims_list = (800, 600)
        create_match = GUI.create_or_join()
        created_match = create_match.gui_create_game(dims_list, available_features)

        feature_selection = created_match[1:None]  # talk about exact format with server guys
        match_name = created_match[0]

        tcp.create_match(tcp_sock, game, match_name, feature_selection)

        match_lobby(tcp_sock, server_ip, game, dims_list)

    elif command[0] == "join_match":
        match_name = command[1]
        player_color = command[2]

        # what do we need player_id for??
        player_id = tcp.join_match(tcp_sock, match_name, player_color)

        # wait for match_started message from server
        # with the ifo of the port number for udp game traffic
        byte_match_info = tcp_sock.recv(200)
        match_info = byte_match_info.decode("ASCII")
        match_info.split()
        if match_info[0] == "MATCH_STARTED":
            udp_port = match_info[1]
            player_colors = match_info[2]  # player_colors has form like: 1,117,112,179,2,27,158,119

            # todo: call game gui from here with the udp port number
            #  and the server_ip we know from the broadcast
            # was hat server_ip usw mit der game gui zu tun?
            game_gui = GUI.Game_Gui()
            game_gui.__init__(game_gui, dims_list)
            while True:
                (playerRects, opponentRects, ball, playerScore, opponentScore, DIMS_list) = udp_sock.recvfrom(server_ip,
                                                                                                              udp_poort)
                game_gui._render_screen(game_gui, playerRects, opponentRects, ball, playerScore, opponentScore,
                                        DIMS_list)