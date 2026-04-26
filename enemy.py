import pygame
import random
from settings import WIDTH, HEIGHT
import math


class Enemy:
    def __init__(self, wave, enemy_type, cam_x, cam_y, forced_side=None):
        self.type = enemy_type
        self.damage = 25 + wave * 0.5

        size = 15

        view_left = int(cam_x)
        view_right = int(cam_x + WIDTH)
        view_top = int(cam_y)
        view_bottom = int(cam_y + HEIGHT)

        side = forced_side if forced_side else random.choice(
            ["top", "bottom", "left", "right"]
        )

        x, y = 0, 0  # 🔥 GARANTE SEMPRE VALOR

        if side == "top":
            x = random.randint(int(view_top), int(view_bottom))
            y = view_top - size

        elif side == "bottom":
            x = random.randint(int(view_top), int(view_bottom))
            y = view_bottom + size

        elif side == "left":
            x = view_left - size
            y = random.randint(int(view_top), int(view_bottom))

        elif side == "right":
            x = view_right + size
            y = random.randint(int(view_top), int(view_bottom))

        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = self.pos

        # base stats
        self.color = (255, 30, 0)
        self.speed = 1.5 + wave * 0.1
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

    def move_towards(self, player, neighbors):
        # 🎯 direção base (player)
        dx = player.pos.x - self.pos.x
        dy = player.pos.y - self.pos.y

        move_dir = pygame.Vector2(dx, dy)

        if move_dir.length() > 0:
            move_dir = move_dir.normalize()

        # 🧲 separação
        separation = pygame.Vector2(0, 0)

        for other in neighbors:
            if other == self:
                continue

            dx = self.pos.x - other.pos.x
            dy = self.pos.y - other.pos.y

            dist = math.hypot(dx, dy)

            min_dist = (self.rect.width + other.rect.width) / 2

            if dist < min_dist and dist > 0:
                push = pygame.Vector2(dx, dy) / dist
                separation += push

        if separation.length() > 0:
            separation = separation.normalize()

        # ⚖️ mistura (ajusta aqui!)
        final_dir = move_dir + separation * 0.7

        if final_dir.length() > 0:
            final_dir = final_dir.normalize()

        # 🚀 movimento FINAL (uma vez só)
        self.pos += final_dir * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, screen, cam_x, cam_y):
        pygame.draw.rect(
            screen,
            self.color,
            (
                int(self.pos.x - cam_x - self.rect.width // 2),
                int(self.pos.y - cam_y - self.rect.height // 2),
                self.rect.width,
                self.rect.height
            )
        )
