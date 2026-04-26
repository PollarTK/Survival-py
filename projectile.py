import pygame
import math
from settings import PROJECTILE_SPEED
import random


class Projectile:
    def __init__(self, x, y, target, damage):
        self.rect = pygame.Rect(x, y, 5, 5)
        self.speed = PROJECTILE_SPEED
        self.target = target
        dx = target.rect.centerx - x
        dy = target.rect.centery - y
        self.trail = []
        self.max_trail = 10  # tamanho do rastro
        self.damage = damage
        self.is_critical = False
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x, y, 5, 5)

        dist = math.hypot(dx, dy)
        if dist != 0:
            self.vx = dx / dist * self.speed
            self.vy = dy / dist * self.speed

        dx = target.rect.centerx - x
        dy = target.rect.centery - y

        dist = math.hypot(dx, dy)

        if dist != 0:
            direction = pygame.Vector2(dx, dy) / dist
            self.velocity = direction * self.speed
        else:
            self.velocity = pygame.Vector2(0, 0)

    def update(self, enemies):
        if self.target not in enemies:
            self.target = None

        self.trail.append(self.rect.center)
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        if self.target:
            dx = self.target.pos.x - self.pos.x
            dy = self.target.pos.y - self.pos.y

            dist = math.hypot(dx, dy)

            if dist > 0:
                direction = pygame.Vector2(dx, dy) / dist
                self.velocity = direction * self.speed

        self.pos += self.velocity
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        return True

    def draw(self, screen, cam_x, cam_y):
        # 🎯 define cor primeiro
        color = (255, 255, 0)

        if self.is_critical:
            color = (250, 0, 250)

        # 🔥 rastro
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))

            surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, alpha), (5, 5), 3)

            screen.blit(
                surf,
                (pos[0] - cam_x - 5, pos[1] - cam_y - 5)
            )

        # 💥 projétil
        pygame.draw.rect(
            screen,
            color,
            (
                int(self.pos.x - cam_x - self.rect.width // 2),
                int(self.pos.y - cam_y - self.rect.height // 2),
                self.rect.width,
                self.rect.height
            )
        )
