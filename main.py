import pygame
from pygame import mixer
from models import Player

# Initializations
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
HEIGHT = screen.get_height()
WIDTH = screen.get_width()
mixer.music.load("assets/background.wav")
mixer.music.play(-1)


# Constants
GRAVITY = 400
RADIUS_OF_CIRCLE = 10
dt = 0.0



def gameArea():
    player1 = Player(WIDTH / 2, HEIGHT / 2,RADIUS_OF_CIRCLE)
    player2 = Player(WIDTH / 2, HEIGHT /2,RADIUS_OF_CIRCLE)
    player3 = Player(WIDTH / 2, HEIGHT /2,RADIUS_OF_CIRCLE)




    #assets loading
    cloud1 = pygame.transform.scale(pygame.image.load('assets/cloud1.png'),(400,200))


    platforms = [
        pygame.Rect(0,HEIGHT-10,WIDTH,10),
        pygame.Rect(0,HEIGHT-100,WIDTH/2,10),
        pygame.Rect(WIDTH*0.25,HEIGHT-200,WIDTH/2,10),
    ]


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        pygame.draw.circle(screen, "red", player1.pos, RADIUS_OF_CIRCLE)
        pygame.draw.circle(screen, "yellow", player2.pos, RADIUS_OF_CIRCLE)
        pygame.draw.circle(screen, "blue", player3.pos, RADIUS_OF_CIRCLE)
        # pygame.draw.circle(screen, "yellow", (0,0), 20)

        for platform in platforms:
            pygame.draw.rect(screen, "orange", platform)

        # screen.blit(cloud1, (0,0),)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            player1.jump()
        if keys[pygame.K_a]:
            player1.move_left()
        if keys[pygame.K_d]:
            player1.move_right()

        if keys[pygame.K_UP]:
            player2.jump()
        if keys[pygame.K_LEFT]:
            player2.move_left()
        if keys[pygame.K_RIGHT]:
            player2.move_right()

        if keys[pygame.K_8]:
            player3.jump()
        if keys[pygame.K_4]:
            player3.move_left()
        if keys[pygame.K_6]:
            player3.move_right()


        player1.update(dt,platforms)
        player2.update(dt,platforms)
        player3.update(dt,platforms)
        tick = clock.tick(60) # Caps Framerate to 60
        dt = tick / 1000
        pygame.display.flip()



pygame.quit()


