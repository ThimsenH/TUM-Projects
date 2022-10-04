from server_functions.lock_object import LockObject


class Client:
    """a class that holds the information about one client."""
    def __init__(self, ip_addr):
        self.udp = None  # udp thread  of client
        self.tcp = None  # tcp thread of client
        self.ip_addr = ip_addr  # ip-address and port
        self.user_name = None
        self.player_id = None
        self.player = None  # the Player object that belongs to the client
        self.i_am_ready = False
        self.interupt_case = 0
        self.match = None
        self.color = None

        # values for game
        # TODO: Hier muss die richtige Startposition angegeben werden (Y = 320 bei beiden Playern, X = 50 für Player 1, X = 750 für Player 2
        self.position = LockObject([0, 0, 0, 0])  # a list of the current position by the player, and their speed in X (should  always be 0) and Y direction
        self.keys_pressed = LockObject([])  # a list of all the keys currently pressed by the player

