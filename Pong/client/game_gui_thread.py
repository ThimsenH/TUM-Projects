import threading
import pygame
import pygame.locals
import sys
import socket
from server_functions.lock_object import LockObject
import global_settings
from server_functions import help_functions as hf
from random import randrange


class GameObjects:
    """a class to store the game objects accessed by udp and gui as lock objects"""
    def __init__(self):
        self.current_pressed_keys = LockObject([])  # the list of all the currently pressed keys

        self.ball_rect = LockObject(pygame.Rect(300, 300, 15, 15))
        self.player_rect = LockObject(pygame.Rect(50, 260, 10, 140))
        self.opponent_rect = LockObject(pygame.Rect(600, 260, 10, 140))
        self.left_player_score = LockObject(0)
        self.right_player_score = LockObject(0)

        # Powerup boxes
        self.box_rect1 = LockObject(pygame.Rect(220, 3000, 50, 50))
        self.box_rect2 = LockObject(pygame.Rect(550, 3000, 50, 50))

        self.match_running = True  # this needs to be set to false if a GAME_ENDED msg is received and therefor all the game threads should be closed


class GameGUI(pygame.sprite.Sprite):
    """GUI to display the game

    this always needs to be called from the main Thread.
    Otherwise it can lead to problems with render and getting the pressed keys
    """

    def __init__(self, dims, game_objects: GameObjects, lobby,player_color,opponent_color):
        """

        Args:
            dims: dimensions sent by the server
            game_objects: the object for storing all the game relevant data to share between this and the UDP Thread
            lobby: access to the mother object (mainly to access tcp.i_am_ready)
        """
        self.dims = dims
        self.game_objects = game_objects
        self.lobby = lobby
        self.screen = pygame.display.set_mode((dims[0], dims[1]))
        pygame.font.init()
        self.font = pygame.font.SysFont("Times", 50)
        self.ready2play = False
        self._clock = pygame.time.Clock()
        self.Opponent_ID = None
        self.Player_ID = None
        self.player_color = player_color
        self.opponent_color= opponent_color


        # PowerUp Boxes animation
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.images.append(pygame.image.load("client/PowerUp_Frame1.png"))
        self.images.append(pygame.image.load("client/PowerUp_Frame2.png"))
        self.images.append(pygame.image.load("client/PowerUp_Frame3.png"))
        self.images.append(pygame.image.load("client/PowerUp_Frame4.png"))
        self.images.append(pygame.image.load("client/PowerUp_Frame5.png"))
        self.images.append(pygame.image.load("client/PowerUp_Frame6.png"))
        self.index = 0
        self.image = self.images[self.index]

        self.game_ended_reason = None

    def run(self):
        while self.game_objects.match_running is True:
            # Check which keys were pressed and if the player ended the game
            self._process_key_events()

            # Render the current state to the screen
            self._render_screen()
            self.update_score()
            self._clock.tick(60)

        self._show_game_ended_msg()
        pygame.display.quit()
        print("Pygame ended because game is not running anymore")  # TODO close GUI

    def _show_game_ended_msg(self):
        game_ended_text = ' '.join(self.game_ended_reason)
        font = pygame.font.SysFont('Times', 32)

        game_ended_text = font.render(game_ended_text, True, (255, 255, 255))  #
        press_enter_to_continue_text = font.render("press Enter to return to Lobby", True, (255, 255, 255))

        # while True: TODO make this with press enter to return to lobby
            # draw the same text until ENTER is pressed

            # needed to draw again and again because otherwise Windows thinks the screen is frozen
        self.screen.fill((0, 0, 0))
        self.screen.blit(game_ended_text, (10, 50))
        # self.screen.blit(press_enter_to_continue_text, (10, 200))
        pygame.display.flip()

            # keys_pressed = []
            # key = pygame.key.get_pressed()
            # if key[pygame.K_KP_ENTER]:
            #     break
            # elif key[pygame.K_RETURN]:
            #     break
            # self._clock.tick(60)
        pygame.time.wait(5000)

    def _process_key_events(self):
        keys_pressed = []
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                self.lobby.tcp_during_game.from_user_messages.lock.acquire()
                self.lobby.tcp_during_game.from_user_messages.value = ["LEAVING_MATCH Player Quit"]
                self.lobby.tcp_during_game.from_user_messages.lock.release()
                pygame.quit()
                sys.exit()
        key = pygame.key.get_pressed()
        if key[pygame.K_UP]:
            keys_pressed.append("UP")
        elif key[pygame.K_DOWN]:
            keys_pressed.append("DOWN")
        elif key[pygame.K_SPACE]:
            keys_pressed.append("SPACE")
            if self.ready2play is False:
                self.lobby.tcp.send_i_am_ready()
                self.ready2play = True

        self.game_objects.current_pressed_keys.write_value(keys_pressed)

    def _render_screen(self):
        # get current object rects thread safe
        ball = self.game_objects.ball_rect.get_value()
        player = self.game_objects.player_rect.get_value()
        opponent = self.game_objects.opponent_rect.get_value()
        left_player_score = self.game_objects.left_player_score.get_value()
        right_player_score = self.game_objects.right_player_score.get_value()
        # draw the current img
        self.screen.fill((0, 0, 0))
        pygame.draw.aaline(self.screen, (255, 255, 255), (self.dims[0] / 2, 0), (self.dims[0] / 2, self.dims[1]))
        pygame.draw.ellipse(self.screen, (255, 255, 255), ball)
        self.screen.blit(self.font.render(str(left_player_score), -1, (255, 255, 255)), (200, 25))
        self.screen.blit(self.font.render(str(right_player_score), -1, (255, 255, 255)), (600, 25))
        pygame.draw.rect(self.screen, self.player_color , player)
        #self.player_color
        pygame.draw.rect(self.screen, self.opponent_color, opponent)
        self._draw_boxes()
        pygame.display.flip()

    def update_score(self):
        self.lobby.tcp_during_game.from_server_messages.lock.acquire()
        try:
            server_message = self.lobby.tcp_during_game.from_server_messages.value.popleft()
            if server_message[0] == "SCORE_UPDATE":
                if server_message[1] == "1":
                    self.game_objects.left_player_score.lock.acquire()
                    self.game_objects.left_player_score.value = server_message[2]
                    self.game_objects.left_player_score.lock.release()
                else:
                    self.game_objects.right_player_score.lock.acquire()
                    self.game_objects.right_player_score.value = server_message[2]
                    self.game_objects.right_player_score.lock.release()
            elif server_message[0] == "GAME_ENDED":
                # TODO show the message somewhere
                self.game_ended_reason = server_message[1:]
                self.game_objects.match_running = False
        except IndexError:
            pass
        finally:
            self.lobby.tcp_during_game.from_server_messages.lock.release()

    def _draw_boxes(self):
        self.box_rect1 = self.game_objects.box_rect1.get_value()
        self.box_rect2 = self.game_objects.box_rect2.get_value()

        self.screen.blit(self.image, self.box_rect1)
        self.screen.blit(self.image, self.box_rect2)
        # animation
        # when the update method is called, we will increment the index
        self.index += 1

        # if the index is larger than the total images
        if self.index >= len(self.images):
            # we will make the index to 0 again
            self.index = 0

        # finally we will update the image that will be displayed
        self.image = self.images[self.index]
        self.image = pygame.transform.scale(self.image, (50, 50))

class UDPCommunicationThread(threading.Thread):
    """a thread to handle the udp connection from this client to the server"""

    def __init__(self, udp_dst, game_objects: GameObjects):
        threading.Thread.__init__(self)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_dst = udp_dst
        self.game_objects = game_objects
        self.sequence_number_sent = global_settings.START_SEQENCE_NUMBER
        self.sequence_number_recv = global_settings.START_SEQENCE_NUMBER

    def run(self):
        own_udp_port = 6600 + randrange(100)  # use a random number here so that two clients on the same pc dont use the same port
        print(f"Used own UDP Port: {own_udp_port}")
        self.udp_sock.bind(("", own_udp_port))
        self._send_keys()
        self.udp_sock.settimeout(0.1)
        while self.game_objects.match_running is True:
            try:
                recv_data, addr = self.udp_sock.recvfrom(global_settings.BUFF_SIZE)
                message_list = hf.decode_answer(recv_data)
                for element in message_list:
                    self._update_positions(element) #todo handle all messages in this function? -> also for example feature increase board size?
                recv_data, addr = self.udp_sock.recvfrom(global_settings.BUFF_SIZE)
                message_list = hf.decode_answer(recv_data)
                for element in message_list:
                    self._update_positions(
                        element)  # todo handle all messages in this function? -> also for example feature increase board size?
                recv_data, addr = self.udp_sock.recvfrom(global_settings.BUFF_SIZE)
                message_list = hf.decode_answer(recv_data)
                for element in message_list:
                    self._update_positions(
                        element)  # todo handle all messages in this function? -> also for example feature increase board size?
                recv_data, addr = self.udp_sock.recvfrom(global_settings.BUFF_SIZE)
                message_list = hf.decode_answer(recv_data)
                for element in message_list:
                    self._update_positions(
                        element)  # todo handle all messages in this function? -> also for example feature increase board size?
            except socket.timeout:
                pass
            except ConnectionResetError:
                print("UDP Socket was closed by the server")
                self.game_objects.game_running = False
                break
            finally:
                self._send_keys()
        self.udp_sock.close()
        print("UDP Socket closed because game is not running anymore")

    def _update_positions(self, recv_message_list: list):
        # first check with sequence number is message is up to date
        if len(recv_message_list)>1:
            if int(recv_message_list[0]) <= self.sequence_number_recv:
                print("received old UDP Message (sequence number was smaller then already received")
            else:
                self.sequence_number_recv = int(recv_message_list[0])
                # maybe also print a message if the new message is two times older then the expected one
            if recv_message_list[1] == "UPDATE_BALL":
                self.game_objects.ball_rect.lock.acquire()
                self.sign = self.game_objects.ball_rect.value.x
                self.game_objects.ball_rect.value.x = int(recv_message_list[3])
                self.dir= self.sign*int(recv_message_list[3])
                self.game_objects.ball_rect.value.y = int(recv_message_list[4])
                self.game_objects.ball_rect.lock.release()
            elif recv_message_list[1] == "UPDATE_PLAYER":
                if int(recv_message_list[2]) == 1:
                    self.game_objects.player_rect.lock.acquire()
                    self.game_objects.player_rect.value.x = int(recv_message_list[3])
                    self.game_objects.player_rect.value.y = int(recv_message_list[4])
                    self.game_objects.player_rect.lock.release()
                elif int(recv_message_list[2]) == 2:  # TODO replace this with opponent player id
                    self.game_objects.opponent_rect.lock.acquire()
                    self.game_objects.opponent_rect.value.x = int(recv_message_list[3])
                    self.game_objects.opponent_rect.value.y = int(recv_message_list[4])
                    self.game_objects.opponent_rect.lock.release()
                else:
                    pass  # TODO some error management
            elif recv_message_list[1] == "UPDATE_POWERUPS":
                self.game_objects.box_rect1.lock.acquire()
                self.game_objects.box_rect2.lock.acquire()
                self.game_objects.box_rect1.value.x = int(recv_message_list[2])
                self.game_objects.box_rect1.value.y = int(recv_message_list[3])
                self.game_objects.box_rect2.value.x = int(recv_message_list[4])
                self.game_objects.box_rect2.value.y = int(recv_message_list[5])
                self.game_objects.box_rect1.lock.release()
                self.game_objects.box_rect2.lock.release()
            else:
                pass  # TODO some error management

    def _send_keys(self):
        current_keys = self.game_objects.current_pressed_keys.get_value()
        message = f"{self.sequence_number_sent} KEYS_PRESSED {hf.pylist2protlist(current_keys)}"
        self.udp_sock.sendto(message.encode(global_settings.STANDARD_ENCODING), self.udp_dst)
        self.sequence_number_sent += 1
