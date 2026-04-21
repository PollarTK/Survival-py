import pygame
import random
from settings import WIDTH, HEIGHT
import math


class Enemy:
    def __init__(self, wave, enemy_type, cam_x, cam_y, forced_side=None):
        self.type = enemy_type
        self.damage = 25 + wave * 0.5

        size = 15

        view_left = cam_x
        view_right = cam_x + WIDTH
        view_top = cam_y
        view_bottom = cam_y + HEIGHT

        side = forced_side if forced_side else random.choice(
            ["top", "bottom", "left", "right"]
        )

        x, y = 0, 0  # 🔥 GARANTE SEMPRE VALOR

        if side == "top":
            x = random.randint(view_left, view_right)
            y = view_top - size

        elif side == "bottom":
            x = random.randint(view_left, view_right)
            y = view_bottom + size

        elif side == "left":
            x = view_left - size
            y = random.randint(view_top, view_bottom)

        elif side == "right":
            x = view_right + size
            y = random.randint(view_top, view_bottom)

        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = self.pos

        # base stats
        self.color = (255, 30, 0)
        self.speed = 1.2 + wave * 0.1
        self.hp = 3 + wave * 1
        self.xp_value = int(5 + wave * 1.5)

        # variações
        if enemy_type == "fast":
            self.color = (250, 250, 0)
            self.speed *= 1.5
            self.hp *= 0.7
            self.damage *= 0.8

        elif enemy_type == "tank":
            self.color = (0, 0, 255)
            self.speed *= 0.7
            self.hp *= 2
            self.damage *= 1.5

        elif enemy_type == "boss":
            self.color = (255, 0, 255)
            self.speed = 1
            self.hp = 50 + wave * 5
            self.damage = 15 + wave * 1.5
            self.xp_value = 100

            self.rect = pygame.Rect(0, 0, 60, 60)
            self.rect.center = self.pos

    def move_towards(self, player):
        dx = player.pos.x - self.pos.x
        dy = player.pos.y - self.pos.y

        dist = math.hypot(dx, dy)

        if dist > 0:
            direction = pygame.Vector2(dx, dy)
            direction = direction / dist  # normaliza

            self.pos += direction * self.speed
            self.rect.center = self.pos

    def draw(self, screen, cam_x, cam_y):
        pygame.draw.rect(
            screen,
            self.color,
            (
                self.pos.x - cam_x - self.rect.width // 2,
                self.pos.y - cam_y - self.rect.height // 2,
                self.rect.width,
                self.rect.height
            )
        )
