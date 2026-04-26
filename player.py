import pygame
from settings import PLAYER_SPEED


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 8, 15)
        self.stats = {
            "regen": 0.5,
            "max_hp": 75,
            "hp": 75,
            "speed": 2,
            "damage": 1,
            "attack_speed": 1.0,  # multiplicador
            "projectile_count": 1,
            "range": 1.0,
            "xp_gain": 3.0,
            "magnet": 20,
            "crit_chance": 0.05,   # 5%
            "crit_damage": 1.5,   # 150%
        }
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x, y, 8, 15)
        self.speed = PLAYER_SPEED
        self.xp = 0
        self.level = 1
        self.xp_to_next = 40
        self.invulnerable_time = 0
        self.invul_duration = 500  # ms
        self.last_regen = pygame.time.get_ticks()
        self.regen_delay = 1000  # 2 segundos

    def take_damage(self, amount):
        now = pygame.time.get_ticks()

        if now < self.invulnerable_time:
            return

        self.stats["hp"] -= amount
        self.invulnerable_time = now + self.invul_duration

    def gain_xp(self, amount):
        self.xp += amount

        if self.xp >= self.xp_to_next:
            return self.level_up()

        return False

    def update(self):
        now = pygame.time.get_ticks()

        if now - self.last_regen >= self.regen_delay:
            if self.stats["hp"] < self.stats["max_hp"]:
                self.stats["hp"] = min(
                    self.stats["hp"] + self.stats["regen"],
                    self.stats["max_hp"]
                )

                # não ultrapassar o máximo
                if self.stats["hp"] > self.stats["max_hp"]:
                    self.stats["hp"] = self.stats["max_hp"]

            self.last_regen = now

    def level_up(self):
        self.xp -= self.xp_to_next
        self.level += 1
        self.xp_to_next = int(self.xp_to_next * 1.2)

        return True

    def apply_upgrade(self, stat, value):
        if stat in self.stats:
            self.stats[stat] += value

    def move(self, keys):
        direction = pygame.Vector2(0, 0)

        if keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_s]:
            direction.y += 1
        if keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_d]:
            direction.x += 1

        if direction.length() > 0:
            direction = direction.normalize()

        self.pos += direction * self.stats["speed"]
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, screen, cam_x, cam_y):
        now = pygame.time.get_ticks()

        if now < self.invulnerable_time:
            if (now // 100) % 2 == 0:
                return

        pygame.draw.rect(
            screen,
            (0, 100, 255),
            (
                int(self.pos.x - cam_x - self.rect.width // 2),
                int(self.pos.y - cam_y - self.rect.height // 2),
                self.rect.width,
                self.rect.height
            )
        )
