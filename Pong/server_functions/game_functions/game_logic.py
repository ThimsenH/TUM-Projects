"""the logic for the game_functions pong.

This logic is based on the example provided and adapted for multiplayer.
"""

import pygame
import math




class Logic(object):
    """
    in this class all the calculations for the logic are done.

    it takes the players inputs and moves the players accordingly

    it processes the movement of the ball
    """

    def __init__(self, match):
        """

        Args:
            game: the game to which this logic belongs. Needed to access the Player Objects
        """
        self.match = match
        self.player1Rects = {
            -60: pygame.Rect(50, 380, 10, 20),  # Bottom of paddle
            -45: pygame.Rect(50, 360, 10, 20),
            -30: pygame.Rect(50, 340, 10, 20),
            -0: pygame.Rect(50, 320, 10, 20),  # Middle of Paddle with (X, Y, width, length)
            30: pygame.Rect(50, 300, 10, 20),
            45: pygame.Rect(50, 280, 10, 20),
            60: pygame.Rect(50, 260, 10, 20),  # Top of paddle
        }

        self.player2Rects = {
            -60: pygame.Rect(750, 380, 10, 20),  # Bottom of paddle
            -45: pygame.Rect(750, 360, 10, 20),
            -30: pygame.Rect(750, 340, 10, 20),
            -0: pygame.Rect(750, 320, 10, 20),  # Middle of Paddle with (X, Y, width, length)
            30: pygame.Rect(750, 300, 10, 20),
            45: pygame.Rect(750, 280, 10, 20),
            60: pygame.Rect(750, 260, 10, 20),  # Top of paddle
        }

        self.ball = pygame.Rect(400, 300, 5, 5)

        self.ballAngle = math.radians(0)
        self.ballSpeed = 5
        # Ball speed in X direction for communication with clients
        self.ballSpeedX = self.ballSpeed * math.cos(self.ballAngle)
        # Ball speed in Y direction for communication with clients
        self.ballSpeedY = self.ballSpeed * -math.sin(self.ballAngle)
        self.player1Score = 0
        self.player2Score = 0
        self.direction = -1
        self.pause = 10
        self.player1speed = 0
        self.player1speedX = 0
        self.player2speed = 0
        self.player2speedX = 0
        self.score_update1 = False
        self.score_update2 = False
        self.player1won = False
        self.player2won = False

        # For computing powerups
        self.multiplicatorsPlayer1 = [1, 1, 1]
        self.multiplicatorsPlayer2 = [1, 1, 1]

        # Arguments for PowerUp calculations
        self.boxRect1 = pygame.Rect(220, 300, 50, 50)
        self.boxRect2 = pygame.Rect(550, 300, 50, 50)

        # Movement speed of powerupboxes in Y direction
        self.stepbox1 = -1
        self.stepbox2 = 1

        self.starttime1 = 0
        self.delta1 = 0

        self.play1_hasPower = False
        self.play2_hasPower = False
        self.play1_PowTime = 0
        self.play2_PowTime = 0
        self.index = 0

    def update_player_positions(self):
        """Update the position of all the players based on the keys currently pressed.

        This currently works only for two players.
        """
        for i, client in enumerate(self.match.client_list):
            key = client.keys_pressed.get_value()
            if i == 0:
                if key is None:
                    self.player1speed = 0
                    pass
                elif "UP" in key:
                    self._move_player1_up()
                elif "DOWN" in key:
                    self._move_player1_down()
            elif i == 1:
                if key is None:
                    self.player2speed = 0
                    pass
                elif "UP" in key:
                    self._move_player2_up()
                elif "DOWN" in key:
                    self._move_player2_down()

    def update_state(self):
        """
        Controlls pause buffer, updates ball if pause is not active
        """

        if self.pause:
            self.pause -= 1
        else:
            self._update_ball()

    def write_positions(self):
        """Write the current positions to the Lock Objects, so that they can be sent by the udp_thread."""
        # Update the positions threadsafe in the players Object
        for i, client in enumerate(self.match.client_list):
            player_number = i + 1
            if player_number == 1:
                position = [self.player1Rects[60].x, self.player1Rects[60].y, self.player1speedX, self.player1speed]
            elif player_number == 2:
                position = [self.player2Rects[60].x, self.player2Rects[60].y, self.player2speedX, self.player2speed]
            else:
                raise KeyError("Logic wanted to write position to unknown client")

            client.position.write_value(position)

        # update the balls position threadsafe
        ball_position = [0, self.ball.x, self.ball.y, self.ballSpeedX, self.ballSpeedY]
        self.match.ball_position.write_value(ball_position)

    def write_powerup_positions(self):
    # update the powerup box position
        powerup_positions = [self.boxRect1.x, self.boxRect1.y, self.boxRect2.x, self.boxRect2.y]
        self.match.powerup_positions.write_value(powerup_positions)

    def _move_player1_up(self):
        if self.player1Rects[60].y > 0:
            for p1Rect in self.player1Rects:
                self.player1speed = -2 * self.multiplicatorsPlayer1[1] * self.multiplicatorsPlayer1[1] / (self.multiplicatorsPlayer2[1] * self.multiplicatorsPlayer2[1])
                self.player1Rects[p1Rect].y += self.player1speed

    def _move_player1_down(self):
        if self.player1Rects[-60].y < 590:
            for p1Rect in self.player1Rects:
                self.player1speed = +2 * self.multiplicatorsPlayer1[1] * self.multiplicatorsPlayer1[1]/ (self.multiplicatorsPlayer2[1] * self.multiplicatorsPlayer2[1])
                self.player1Rects[p1Rect].y += self.player1speed

    def _move_player2_up(self):
        if self.player2Rects[60].y > 0:
            for p2Rect in self.player2Rects:
                self.player2speed = -2 * self.multiplicatorsPlayer2[2] * self.multiplicatorsPlayer2[2] / (self.multiplicatorsPlayer1[2] * self.multiplicatorsPlayer1[2])
                self.player2Rects[p2Rect].y += self.player2speed

    def _move_player2_down(self):
        if self.player2Rects[-60].y < 590:
            for p2Rect in self.player2Rects:
                self.player2speed = +2 * self.multiplicatorsPlayer2[2] * self.multiplicatorsPlayer2[2] / (self.multiplicatorsPlayer1[2] * self.multiplicatorsPlayer1[2])
                self.player2Rects[p2Rect].y += self.player2speed

    def _update_ball(self):
        if self.ball.y <= 0 or self.ball.y > 595:
            self.ballAngle *= -1
        self.ball.x += self.direction * self.ballSpeed * self.multiplicatorsPlayer1[0] * self.multiplicatorsPlayer2[0] * math.cos(self.ballAngle)
        self.ball.y += self.direction * self.ballSpeed * self.multiplicatorsPlayer1[0] * self.multiplicatorsPlayer2[0] * -math.sin(self.ballAngle)
        if self.ball.x > 800 or self.ball.x < 0:
            if self.ball.x > 800:
                self.player1Score += 1
                self.score_update1 = True

            elif self.ball.x < 0:
                self.player2Score += 1
                self.score_update2 = True
            self.ball.x = 400
            self.ball.y = 300
            self.ballAngle = math.radians(0)
            self.pause = 40
            self.play1_PowTime = 0
            self.play2_PowTime = 0

            if self.player2Score >= 11 or self.player1Score >= 11:
                if self.player1Score >= 11:
                    self.player1won = True
                if self.player2Score >= 11:
                    self.player2won = True
            return

        if self.direction < 0:
            for p1Rect in self.player1Rects:
                if self.player1Rects[p1Rect].colliderect(self.ball):
                    self.ballAngle = math.radians(p1Rect)
                    self.direction = 1
                    break

        else:
            for p2Rect in self.player2Rects:
                if self.player2Rects[p2Rect].colliderect(self.ball):
                    self.ballAngle = -1 * math.radians(p2Rect)
                    self.direction = -1

    # PowerUp Logic
    def get_powerup_state(self):
        # Activates if one player hits a powerup; ends when PowTime = 0
        if self.play1_hasPower:
            self.play1_PowTime -= 1
            if self.play1_PowTime > 0:
                self.multiplicatorsPlayer1[self.index] = 2
            else:
                self.play1_hasPower = False
                self.multiplicatorsPlayer1[self.index] = 1
                self.index = (self.index + 1) % 3
                print("ENDE POWERUP1")
        if self.play2_hasPower:
            self.play2_PowTime -= 1
            if self.play2_PowTime > 0:
                self.multiplicatorsPlayer2[self.index] = 2
            else:
                self.play2_hasPower = False
                self.multiplicatorsPlayer2[self.index] = 1
                self.index = (self.index + 1) % 3
                print("ENDE POWERUP2")

    def update_box1(self):
        # Movement of powerup box
        if self.boxRect1.y <= 0:
            self.stepbox1 = 1
        elif self.boxRect1.y > 550:
            self.stepbox1 = -1
        self.boxRect1.y += self.stepbox1

        # collision with box
        if self.direction > 0:
            if self.ball.colliderect(self.boxRect1):
                print("PowerUp Player 1 Hit Box 1")
                self.boxRect1.y = 2500
                self.play1_hasPower = True
                self.play1_PowTime = 120
            else:
                pass
        else:
            if self.ball.colliderect(self.boxRect1):
                print("PowerUp Player 2 Hit Box 1")
                self.boxRect1.y = 2500
                self.play2_hasPower = True
                self.play2_PowTime = 120
            else:
                pass

    def update_box2(self):
        # Movement of powerup box
        if self.boxRect2.y <= 0:
            self.stepbox2 = 1
        elif self.boxRect2.y > 550:
            self.stepbox2 = -1
        self.boxRect2.y += self.stepbox2

        # collision with box
        if self.direction > 0:
            if self.ball.colliderect(self.boxRect2):
                self.boxRect2.y = 2500
                print("PowerUp Player 1 Hit Box 2")
                self.play1_hasPower = True
                self.play1_PowTime = 120
            else:
                pass
        else:
            if self.ball.colliderect(self.boxRect2):
                self.boxRect2.y = 2500
                print("PowerUp Player 2 Hit Box 2")
                self.play2_hasPower = True
                self.play2_PowTime = 120
            else:
                pass

