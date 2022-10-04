# PYGAME template
import pygame
import time





WIDTH = 600
HEIGHT = 600
FPS = 30

# define colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


# animation


class Box(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.images.append(pygame.image.load('frame 1.png'))
        self.images.append(pygame.image.load('frame 2.png'))
        self.images.append(pygame.image.load('frame 3.png'))
        self.images.append(pygame.image.load('frame 4.png'))
        self.images.append(pygame.image.load('frame 5.png'))
        self.images.append(pygame.image.load('frame 6.png'))
        self.index = 0
        self.image = self.images[self.index]

        #self.image1 = pygame.Surface((100, 100))
        #self.image1.blit(self.image, (0, 0))


        self.rect =  pygame.Rect(250, 255, 100, 100) #self.image1.get_rect()
        #self.rect.center = (int(WIDTH / 2), int(HEIGHT / 2))
        self.step = 5



    def update(self):
        #animation
        # when the update method is called, we will increment the index
        self.index += 1

        # if the index is larger than the total images
        if self.index >= len(self.images):
            # we will make the index to 0 again
            self.index = 0

        # finally we will update the image that will be displayed
        self.image = self.images[self.index]
        self.image = pygame.transform.scale(self.image, (100, 100))



        #Movement of box
        if self.rect.top == 0:
            self.step = 5
        elif self.rect.bottom == HEIGHT:
            self.step = -5
        self.rect.y += self.step
        print(self.rect.y, self.rect.top, self.rect.bottom)


