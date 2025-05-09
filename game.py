import datetime
import os
import pygame
import sys
import random

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (127, 127, 127)
GOLD = (255, 215, 0)


# Inicjalizacja Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Projekt na potrzeby SGD")
clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsans", 36)

# Gracz
player_pos = pygame.Vector2(400, 300)
player_speed = 222
player_radius = 20
player_hp = 3
score = 0
score_font = pygame.font.SysFont("comicsans", 24)
leaderboard_file = "leaderboard.txt"

# Pociski
bullets = []
bullet_speed = 400
fire_interval = 500
last_shot_time = pygame.time.get_ticks()

# Dekoracje
decor = []
decor_images = []

# Przeciwnicy
enemy_radius = 16
enemy_speed = 200
enemies = []

# Stan gry
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
    global player_pos, bullets, last_shot_time, player_hp
    player_pos = pygame.Vector2(400, 300)
    bullets.clear()
    last_shot_time = pygame.time.get_ticks()
    player_hp = 3
    spawn_enemies(10)

def draw_gradient_background():
    for y in range(600):
        color = (0, int(100 + (y / 600) * 155), 0)
        pygame.draw.line(screen, color, (0, y), (800, y))

def load_decor():
    for image_file in os.listdir('assets/decor/'):
        image = pygame.image.load(os.path.join('assets/decor/', image_file)).convert_alpha()
        image = pygame.transform.scale(image, (32, 32))
        decor_images.append(image)
    for i in range(20):
        x = random.randrange(0, 800 - 32)
        y = random.randrange(0, 600 - 32)
        image = random.choice(decor_images)
        decor.append((image, x, y))

def spawn_enemies(count):
    enemies.clear()
    for _ in range(count):
        while True:
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            if pygame.Vector2(x, y).distance_to(player_pos) > 150:
                break
        enemies.append({"pos": pygame.Vector2(x, y)})

def reset_game():
    global player_pos, bullets, last_shot_time, player_hp, score
    player_pos = pygame.Vector2(400, 300)
    bullets.clear()
    last_shot_time = pygame.time.get_ticks()
    player_hp = 3
    score = 0
    spawn_enemies(10)

def save_score():
    with open(leaderboard_file, "a") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{now} - {score}\n")

def load_leaderboard():
    if not os.path.exists(leaderboard_file):
        return []
    with open(leaderboard_file, "r") as f:
        lines = f.readlines()[-5:]
    return [line.strip() for line in lines]


# Ładowanie dekoracji
load_decor()

# Pętla gry
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN:
                state = "play"


        elif state == "game_over":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                state = "start"

        elif state == "play":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "pause"

        elif state == "victory":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                state = "start"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

    if state == "start":
        draw_text("Press any key to start", (400, 300))
        draw_text("WASD to move, mouse to aim", (400, 350))
        draw_text("Press Q to quit", (400, 400))

    elif state == "pause":
        draw_text("Game Paused", (400, 300))
        draw_text("Press ANY KEY to resume", (400, 350))
        draw_text("Press Q to quit", (400, 400))

    elif state == "game_over":
        draw_text("Game Over", (400, 150), RED)
        draw_text(f"Your score: {score}", (400, 200), GOLD)
        draw_text("Press R to restart", (400, 280), GREY)
        leaderboard = load_leaderboard()
        draw_text("Leaderboard:", (400, 320), WHITE)
        for i, line in enumerate(leaderboard):
            draw_text(line, (400, 350 + i * 30), WHITE)


    elif state == "victory":
        draw_text("You Win!", (400, 150), GREEN)
        draw_text(f"Your score: {score}", (400, 200), GOLD)
        draw_text("Press R to restart", (400, 280), GREY)
        leaderboard = load_leaderboard()
        draw_text("Leaderboard:", (400, 320), WHITE)
        for i, line in enumerate(leaderboard):
            draw_text(line, (400, 350 + i * 30), WHITE)

    elif state == "play":
        # Sterowanie gracza
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y = -1
        if keys[pygame.K_s]: move.y = 1
        if keys[pygame.K_a]: move.x = -1
        if keys[pygame.K_d]: move.x = 1
        if move.length_squared() > 0:
            move = move.normalize()
            player_pos += move * player_speed * dt

        # Strzelanie
        now = pygame.time.get_ticks()
        if now - last_shot_time > fire_interval:
            shoot_bullet(player_pos, pygame.Vector2(pygame.mouse.get_pos()))
            last_shot_time = now

        # Aktualizacja pocisków
        for bullet in bullets:
            bullet["pos"] += bullet["dir"] * bullet_speed * dt

        # Kolizje pocisków z przeciwnikami
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet["pos"].distance_to(enemy["pos"]) < enemy_radius:
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 10
                    if not enemies:
                        state="victory"
                    break

        # Ruch przeciwników + kolizje z graczem
        for enemy in enemies[:]:
            direction = (player_pos - enemy["pos"]).normalize()
            enemy["pos"] += direction * enemy_speed * dt

            if enemy["pos"].distance_to(player_pos) < (player_radius + enemy_radius):
                enemies.remove(enemy)
                player_hp -= 1
                if player_hp <= 0:
                    save_score()
                    state = "game_over"

        # Rysowanie tła i dekoracji
        draw_gradient_background()
        for i in decor:
            screen.blit(i[0], (i[1], i[2]))

        # Gracz
        player_image = pygame.image.load("player.png").convert_alpha()
        player_image = pygame.transform.scale(player_image, (player_radius * 2, player_radius * 2))
        screen.blit(player_image, player_pos)

        enemy_image = pygame.image.load("tmp.png").convert_alpha()
        enemy_image = pygame.transform.scale(enemy_image, (enemy_radius * 2, enemy_radius * 4))
        for enemy in enemies:
            screen.blit(enemy_image, enemy["pos"] - pygame.Vector2(enemy_radius, enemy_radius))

        # Przeciwnicy
        #for enemy in enemies:
        #   pygame.draw.circle(screen, BLUE, (int(enemy["pos"].x), int(enemy["pos"].y)), enemy_radius)

        # Pociski
        for bullet in bullets:
            pygame.draw.rect(screen, RED, (*bullet["pos"], 5, 5))

        # HP
        draw_text(f"HP: {player_hp}", (60, 30), RED)

        # Wynik
        draw_text(f"Score: {score}", (700, 30), GOLD)

    pygame.display.flip()

pygame.quit()
sys.exit()
