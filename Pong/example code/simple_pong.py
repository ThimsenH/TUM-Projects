import pygame

pygame.init()

clock = pygame.time.Clock()
# Screen
screen_width = 1200
screen_length = 600
screen = pygame.display.set_mode((screen_width, screen_length))
pygame.display.set_caption("Pong_Game_Screen")

# Defining the Play tools
ball = pygame.Rect(screen_width / 2 - 15, screen_length / 2 - 15, 30, 30)
player_1 = pygame.Rect(screen_width - 20, screen_length / 2 - 70, 10, 140)
player_2 = pygame.Rect(10, screen_length / 2 - 70, 10, 140)

# Drawing: colors in rgb tupels 0:255
dark_grey = pygame.Color("grey12")
light_grey = (200, 200, 200)

# Physiks
ball_speed_x = 5
ball_speed_y = 5
player_speed = 0


def restart_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (screen_width / 2, screen_length / 2)
    ball_speed_x *= random.choice((1, -1))
    ball_speed_y *= random.choice((1, -1))


def ball_animation():
    global ball_speed_x, ball_speed_y
    ball.x += ball_speed_x
    ball.y += ball_speed_y
    if ball.top <= 0 or ball.bottom >= screen_length:
        ball_speed_y *= -1
    if ball.left <= 0 or ball.right >= screen_width:
        restart_ball()
    if ball.colliderect(player_1) or ball.colliderect(player_2):
        ball_speed_x *= -1


def player_1_animation():
    global player_speed
    player_1.y += player_speed
    if player_1.top <= 0:
        player_1.top = 0
    if player_1.bottom > screen_length:
        player_1.bottom = screen_length


def bot(difficulty):
    if player_2.top + 70 < ball.y:
        player_2.top += 5 * difficulty
    if player_2.bottom - 70 > ball.y:
        player_2.bottom -= 5 * difficulty
    if player_2.top <= 0:
        player_2.top = 0
    if player_2.bottom > screen_length:
        player_2.bottom = screen_length


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                player_speed += 7
            if event.key == pygame.K_UP:
                player_speed -= 7
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player_speed -= 7
            if event.key == pygame.K_UP:
                player_speed += 7

    ball_animation()
    player_1_animation()
    bot(2)

    # Screen Visualisation
    screen.fill(dark_grey)
    pygame.draw.aaline(screen, light_grey, (screen_width / 2, 0), (screen_width / 2, screen_length))
    pygame.draw.rect(screen, light_grey, player_1)
    pygame.draw.rect(screen, light_grey, player_2)
    pygame.draw.ellipse(screen, light_grey, ball)

    # Frames per second
    pygame.display.flip()
    clock.tick(60)

# Features
# Bot
