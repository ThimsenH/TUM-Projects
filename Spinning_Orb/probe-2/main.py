# PYGAME template

from box import *
import pygame
import os

WIDTH = 600
HEIGHT = 600
FPS = 30

# define colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class features:
    def __init__(self):

        # initialize game window, etc
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("My game")
        self.clock = pygame.time.Clock()
        self.running = True




    def new(self):
        # start a new game
        self.all_sprites = pygame.sprite.Group()
        self.box = Box()
        self.all_sprites.add(self.box)
        self.run()

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()

    def events(self):
        # Game Loop - events
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def draw(self):
        # Game Loop - draw
        self.screen.fill(WHITE)
        self.all_sprites.draw(self.screen)
        # *after* drawing everything, flip the display
        pygame.display.flip()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

if __name__ == "__main__":
    game = features()
    game.new()
