import os

import pygame
import math
import sys
import time
import random


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (127, 127, 127)

player_pos = pygame.Vector2(400, 300)
player_speed = 200
player_radius = 20

bullets = []
bullet_speed = 400
fire_interval = 500
last_shot_time = pygame.time.get_ticks()

decor = []
decor_images = []

state = "start"

def draw_text(text, pos, color=WHITE):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=pos)
    screen.blit(surface, rect)

def shoot_bullet(player_pos, mouse_pos):
    direction = (mouse_pos - player_pos).normalize()
    bullet = {
        "pos": pygame.Vector2(player_pos),
        "dir": direction,
    }
    bullets.append(bullet)

def reset_game():
    global player_pos, bullets, last_shot_time
    player_pos = pygame.Vector2(400, 300)
    bullets.clear()
    last_shot_time = pygame.time.get_ticks()

def draw_gradient_background():
    for y in range(600):
        color = (0, int(100 + (y / 600) * 155), 0)
        pygame.draw.line(screen, color, (0, y), (800, y))

def load_decor():
    for i in range(20):
        x = random.randrange(0, 800  - 32)
        y = random.randrange(0, 600 - 32)
        image = random.choice(decor_images)
        decor.append((image, x, y))

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Projekt na potrzeby SGD")
for image_file in os.listdir('assets/decor/'):
    decor_images.append(pygame.image.load(os.path.join('assets/decor/', image_file)).convert_alpha())
    decor_images[-1] = pygame.transform.scale(decor_images[-1], (32, 32))

load_decor()


clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsans", 36)


running = True
while running:
    dt = clock.tick(60) / 1000.0
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            running = False

        if state == "start":
            if event.type == pygame.KEYDOWN:
                state = "play"
                reset_game()

        elif state == "pause":
            if event.type == pygame.KEYDOWN:
                state = "play"

        elif state == "play":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "pause"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                state = "game_over"

    if state == "start":
        draw_text("Press any key to start", (400, 300))
        draw_text("WASD to move, mouse to aim", (400, 350))
        draw_text("Press Q to quit", (400, 400))

    elif state == "pause":
        draw_text("Game Paused", (400, 300))
        draw_text("Press ANY KEY to resume", (400, 350))

    elif state == "game_over":
        draw_text("Game Over", (400, 350))


    elif state == "play":

        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]:    move.y = -1
        if keys[pygame.K_s]:    move.y = 1
        if keys[pygame.K_a]:    move.x = -1
        if keys[pygame.K_d]:    move.x = 1
        if move.length_squared() > 0:
            move = move.normalize()
            player_pos += move * player_speed * dt

        now = pygame.time.get_ticks()
        if now - last_shot_time > fire_interval:
            shoot_bullet(player_pos, pygame.Vector2(pygame.mouse.get_pos()))
            last_shot_time = now

        for bullet in bullets:
            bullet["pos"] += bullet["dir"] * bullet_speed * dt

    #pygame.draw.circle(screen, WHITE, player_pos, player_radius)
        player_image = pygame.image.load("player.png").convert_alpha()
        player_image = pygame.transform.scale(player_image, (player_radius * 2, player_radius * 2))


        draw_gradient_background()
        for i in decor:
            screen.blit(i[0], (i[1], i[2]))

        screen.blit(player_image, player_pos)

        for bullet in bullets:
            pygame.draw.rect(screen, RED, (*bullet["pos"], 5, 5))

    pygame.display.flip()

pygame.time.wait(1000)
pygame.quit()
sys.exit()