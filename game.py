from player import Player
from projectile import Projectile
import settings
from enemy import Enemy
import random
import pygame
import math
from xp_orb import XPOrb
from classes import CLASSES


class Game:
    def __init__(self):
        self.player = Player(settings.WIDTH//2, settings.HEIGHT//2)
        self.last_shot = pygame.time.get_ticks()
        self.last_spawn = pygame.time.get_ticks()
        self.last_orb_spawn = pygame.time.get_ticks()
        self.projectiles = []
        self.enemies = []
        self.xp_orbs = []
        self.upgrade_options = []
        self.wave = 1
        self.kills = 0
        self.kills_to_next_wave = 15
        self.camera_x = 0
        self.camera_y = 0
        self.show_stats = False
        self.spawn_delay = settings.SPAWN_DELAY
        self.state = "menu"
        self.menu_state = "main"   # ✔ só um
        self.selected_class = None
        self.selected_map = None

    def draw_main_menu(self, screen):
        screen.fill((20, 20, 20))

        font = pygame.font.SysFont(None, 50)

        self.play_rect = pygame.Rect(settings.WIDTH//2 - 100, 300, 200, 60)

        pygame.draw.rect(screen, (50, 50, 50), self.play_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.play_rect, 2)

        text = font.render("JOGAR", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=self.play_rect.center))

    def draw_menu(self, screen):

        if self.menu_state == "main":
            self.draw_main_menu(screen)

        elif self.menu_state == "classes":
            self.draw_classes_menu(screen)

    def draw_classes_menu(self, screen):
        screen.fill((20, 20, 20))

        font_title = pygame.font.SysFont(None, 50)
        font = pygame.font.SysFont(None, 28)

        # TÍTULO
        title = font_title.render("Escolha sua Classe", True, (255, 255, 255))
        screen.blit(title, (settings.WIDTH//2 - 180, 80))

        # CARDS
        self.class_rects = []

        start_x = settings.WIDTH//2 - 300
        y = 200
        spacing = 220

        for i, (key, data) in enumerate(CLASSES.items()):
            x = start_x + i * spacing

            rect = pygame.Rect(x, y, 180, 200)
            self.class_rects.append((rect, key))

            # destaque seleção
            color = (70, 70, 70)
            if self.selected_class == key:
                color = (120, 120, 120)

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

            # nome
            text = font.render(data["name"], True, (255, 255, 255))
            screen.blit(text, (x + 40, y + 20))

        # DESCRIÇÃO
        if self.selected_class:
            desc = CLASSES[self.selected_class]["desc"]
            desc_text = font.render(desc, True, (200, 200, 200))
            screen.blit(desc_text, (settings.WIDTH//2 - 200, 450))

        # BOTÃO CONFIRMAR
        self.confirm_rect = pygame.Rect(settings.WIDTH//2 - 100, 500, 200, 50)
        pygame.draw.rect(screen, (50, 100, 50), self.confirm_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.confirm_rect, 2)

        confirm_text = font.render("Confirmar", True, (255, 255, 255))
        screen.blit(confirm_text, confirm_text.get_rect(
            center=self.confirm_rect.center))

        # BOTÃO VOLTAR
        self.back_rect = pygame.Rect(20, 20, 120, 40)
        pygame.draw.rect(screen, (80, 50, 50), self.back_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.back_rect, 2)

        back_text = font.render("Voltar", True, (255, 255, 255))
        screen.blit(back_text, back_text.get_rect(
            center=self.back_rect.center))

    def reset_run(self):
        # limpa entidades
        self.player = Player(settings.WIDTH//2, settings.HEIGHT//2)
        self.enemies = []
        self.projectiles = []
        self.xp_orbs = []

        # reseta progresso
        self.wave = 1
        self.kills = 0
        self.kills_to_next_wave = 15

        # reseta timers
        now = pygame.time.get_ticks()
        self.last_spawn = now
        self.last_shot = now
        self.last_orb_spawn = now

        # câmera
        self.camera_x = 0
        self.camera_y = 0

        # estado
        self.upgrade_options = []

    def handle_click(self, pos):

        # ================= MENU =================
        if self.state == "menu":
            if self.menu_state == "main":
                if self.play_rect.collidepoint(pos):
                    self.menu_state = "classes"

            elif self.menu_state == "classes":

                for rect, key in self.class_rects:
                    if rect.collidepoint(pos):
                        self.selected_class = key

                if self.selected_class and self.confirm_rect.collidepoint(pos):
                    # self.menu_state = "map"
                    self.start_game()

                if self.back_rect.collidepoint(pos):
                    self.menu_state = "main"

            elif self.menu_state == "map":
                if self.selected_class:
                    self.start_game()

        # ================= LEVEL UP =================
        elif self.state == "levelup":

            card_width = 200
            card_height = 100
            spacing = 50

            total_width = 3 * card_width + 2 * spacing
            start_x = (settings.WIDTH - total_width) // 2
            y = settings.HEIGHT // 2 - 50

            for i, upgrade in enumerate(self.upgrade_options):
                x = start_x + i * (card_width + spacing)
                rect = pygame.Rect(x, y, card_width, card_height)

                if rect.collidepoint(pos):
                    self.player.apply_upgrade(
                        upgrade["stat"], upgrade["value"])
                    self.state = "playing"
                    return  # 🔥 IMPORTANTE

    def start_game(self):

        self.reset_run()

        self.player = Player(
            settings.WIDTH//2,
            settings.HEIGHT//2
        )

        data = CLASSES[self.selected_class]

        # aplica stats
        for stat, value in data["stats"].items():
            self.player.stats[stat] = value

        # arma inicial
        self.player.weapon_type = data["weapon"]

        # cor da classe
        self.player.color = data["color"]

        self.state = "playing"

    def draw_ui(self, screen):
        bar_width = 300
        bar_height = 8

        x = (settings.WIDTH - bar_width) // 2
        y = 560

        # ================= XP =================
        pygame.draw.rect(screen, (20, 20, 20), (x, y, bar_width, bar_height))

        xp_ratio = self.player.xp / self.player.xp_to_next
        fill_width = int(bar_width * xp_ratio)

        pygame.draw.rect(screen, (0, 220, 0), (x, y, fill_width, bar_height))
        pygame.draw.rect(screen, (0, 80, 0), (x, y, bar_width, bar_height), 1)

        # ================= HP =================
        pygame.draw.rect(screen, (20, 20, 20),
                         (x, y + 10, bar_width, bar_height))

        hp_ratio = self.player.stats["hp"] / self.player.stats["max_hp"]
        fill_width2 = int(bar_width * hp_ratio)

        pygame.draw.rect(screen, (220, 0, 0),
                         (x, y + 10, fill_width2, bar_height))
        pygame.draw.rect(screen, (80, 0, 0),
                         (x, y + 10, bar_width, bar_height), 1)

        # ================= TEXTO =================
        font = pygame.font.SysFont(None, 16)

        level_text = font.render(
            f"Level {self.player.level}", True, (255, 255, 255)
        )
        level_rect = level_text.get_rect(center=(settings.WIDTH // 2, y - 10))
        screen.blit(level_text, level_rect)

        font = pygame.font.SysFont(None, 20)

        wave_text = font.render(f"Wave {self.wave}", True, (255, 255, 255))

        # canto superior esquerdo
        screen.blit(wave_text, (settings.WIDTH // 2 - 10, 10))

    def spawn_map_orbs(self):
        now = pygame.time.get_ticks()

        if now - self.last_orb_spawn >= settings.ORB_SPAWN_DELAY:
            x = random.randint(0, settings.WIDTH)
            y = random.randint(0, settings.HEIGHT)

            roll = random.random()

            if roll < 0.7:
                value = 1  # comum (70%)
            elif roll < 0.9:
                value = 10  # incomum (20%)
            elif roll < 0.98:
                value = 40  # raro (8%)
            else:
                value = 100  # MUITO raro (2%)

            self.xp_orbs.append(XPOrb(x, y, value))
            self.last_orb_spawn = now

    def merge_orbs(self):
        merged = set()

        for i, orb1 in enumerate(self.xp_orbs):
            if orb1 in merged:
                continue

            for orb2 in self.xp_orbs[i+1:]:
                if orb2 in merged:
                    continue

                # 🔥 decide quem é maior
                if orb1.value >= orb2.value:
                    big = orb1
                    small = orb2
                else:
                    big = orb2
                    small = orb1

                dx = big.pos.x - small.pos.x
                dy = big.pos.y - small.pos.y

                dist = math.hypot(dx, dy)

                # 💥 força de atração
                if dist < 20 and dist > 5:
                    direction = pygame.Vector2(dx, dy)

                    if dist > 0:
                        direction = direction / dist

                    force = 1

                    small.pos += direction * force
                    small.rect.center = small.pos

                # 💥 merge
                if dist <= 5:
                    big.value += small.value
                    big.update_visual()

                    merged.add(small)

        self.xp_orbs = [o for o in self.xp_orbs if o not in merged]

    def spawn_enemy(self):
        if len(self.enemies) < 5 + self.wave:
            enemy_type = "normal"

            if self.wave > 4:
                enemy_type = random.choice(["normal", "fast"])

            if self.wave > 8:
                enemy_type = random.choice(["normal", "fast", "tank"])

            self.enemies.append(
                Enemy(self.wave, enemy_type, self.camera_x, self.camera_y)
            )

    def spawn_horde(self):
        amount = 5 + self.wave * 2  # escala com wave

        for _ in range(amount):
            enemy_type = random.choice(["normal", "fast", "tank"])

            self.enemies.append(
                Enemy(self.wave, enemy_type, self.camera_x, self.camera_y)
            )

    def spawn_boss(self):
        self.enemies.append(
            Enemy(self.wave, "boss", self.camera_x, self.camera_y)
        )

    def start_levelup(self):
        self.state = "levelup"
        pool = [
            {"name": "Velocidade", "stat": "speed", "value": 0.5},
            {"name": "Ataque rápido", "stat": "attack_speed", "value": 0.1},
            {"name": "Mais projéteis", "stat": "projectile_count", "value": 1},
            {"name": "Magnetismo", "stat": "magnet", "value": 20},
            {"name": "EXP gain", "stat": "xp_gain", "value": 0.15},
            {"name": "Dano", "stat": "damage", "value": 1},
            {"name": "Alcance", "stat": "range", "value": 0.1},
            {"name": "Vida Máxima", "stat": "max_hp", "value": 25},
            {"name": "Regeneração", "stat": "regen", "value": 0.5},
            {"name": "Chance Crítica", "stat": "crit_chance",
                "value": random.choice([0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1,])},
            {"name": "Dano Crítico", "stat": "crit_damage", "value": 0.2},
        ]

        if self.player.stats["crit_chance"] >= 1.0:
            pool = [p for p in pool if p["stat"] != "crit_chance"]

        self.upgrade_options = random.sample(pool, 3)

    def shoot(self):
        now = pygame.time.get_ticks()

        delay = settings.SHOOT_DELAY / max(
            0.1,
            self.player.stats["attack_speed"]
        )

        if now - self.last_shot < delay:
            return

        target = self.get_nearest_enemy()

        if not target:
            return

        x = self.player.pos.x
        y = self.player.pos.y

        # ================= WARRIOR =================
        if self.player.weapon_type == "slash":
            damage = self.player.stats["damage"] * 2
            proj = Projectile(x, y, target, damage)
            proj.speed *= 0.7
            proj.rect.width = 12
            proj.rect.height = 12
            self.projectiles.append(proj)

        # ================= RANGER =================
        elif self.player.weapon_type == "arrow":
            count = self.player.stats["projectile_count"] + 2
            for i in range(count):
                offset = (i - count // 2) * 15
                damage = self.player.stats["damage"]
                proj = Projectile(x + offset, y, target, damage)
                proj.speed *= 1.5
                self.projectiles.append(proj)

        # ================= MAGE =================
        elif self.player.weapon_type == "magic":
            damage = self.player.stats["damage"] * 1.5
            proj = Projectile(x, y, target, damage)
            proj.speed *= 0.9
            # visual mágico
            proj.is_magic = True
            self.projectiles.append(proj)

        self.last_shot = now

    def get_nearest_enemy(self):  # ✅ AGORA ESTÁ CERTO
        if not self.enemies:
            return None

        nearest = None
        min_dist = float("inf")

        px, py = self.player.rect.center

        for enemy in self.enemies:
            ex, ey = enemy.rect.center
            dist = math.hypot(ex - px, ey - py)

            if dist < min_dist:
                min_dist = dist
                nearest = enemy

        return nearest

    def draw_stats_panel(self, screen):
        # fundo semi-transparente
        overlay = pygame.Surface(
            (settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # caixa central
        panel_width = 400
        panel_height = 450
        x = (settings.WIDTH - panel_width) // 2
        y = (settings.HEIGHT - panel_height) // 2

        pygame.draw.rect(screen, (30, 30, 30),
                         (x, y, panel_width, panel_height))
        pygame.draw.rect(screen, (80, 80, 80),
                         (x, y, panel_width, panel_height), 2)

        font = pygame.font.SysFont(None, 24)

        # título
        title = font.render("STATUS", True, (255, 255, 255))
        screen.blit(title, (x + 150, y + 20))

        names = {
            "hp": "Vida",
            "max_hp": "Vida Máxima",
            "damage": "Dano",
            "attack_speed": "Velocidade de Ataque",
            "crit_chance": "Chance Crítica",
            "crit_damage": "Dano Crítico",
            "speed": "Velocidade",
            "xp_gain": "Ganho de EXP",
            "projectile_count": "Projéteis",
            "magnet": "Coleta",
            "regen": "Regeneração",
            "range": "Alcance",
        }

        # lista de stats
        start_y = y + 60
        spacing = 30

        for i, (key, value) in enumerate(self.player.stats.items()):
            name = names.get(key, key)

            # 💎 formatação inteligente
            if "chance" in key:
                value_text = f"{int(value * 100)}%"

            elif "crit_damage" in key:
                value_text = f"{int(value * 100)}%"

            elif "speed" in key:
                value_text = f"{round(value, 1)}"

            elif "gain" in key:
                value_text = f"{round(value, 2)}x"

            elif "regen" in key:
                value_text = f"{round(value, 1)}"

            else:
                value_text = f"{int(value)}"

            text = font.render(f"{name}: {value_text}", True, (200, 200, 200))
            screen.blit(text, (x + 40, start_y + i * spacing))

    def draw_levelup(self, screen):
        font = pygame.font.SysFont(None, 30)

        card_width = 200
        card_height = 100
        spacing = 50

        total_width = 3 * card_width + 2 * spacing
        start_x = (settings.WIDTH - total_width) // 2
        y = settings.HEIGHT // 2 - 50

        for i, upgrade in enumerate(self.upgrade_options):
            x = start_x + i * (card_width + spacing)

            rect = pygame.Rect(x, y, card_width, card_height)

            pygame.draw.rect(screen, (40, 40, 40), rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

            text = font.render(upgrade["name"], True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=rect.center))

    def update(self):

        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys)
        self.player.update()
        self.spawn_map_orbs()
        self.camera_x = self.player.pos.x - settings.WIDTH // 2
        self.camera_y = self.player.pos.y - settings.HEIGHT // 2
        cell_size = 60
        grid = {}

        # 🔹 montar grid
        for enemy in self.enemies:
            cell_x = int(enemy.pos.x // cell_size)
            cell_y = int(enemy.pos.y // cell_size)

            key = (cell_x, cell_y)

            if key not in grid:
                grid[key] = []

            grid[key].append(enemy)

        # 🔹 mover inimigos com vizinhos
        for enemy in self.enemies:
            cell_x = int(enemy.pos.x // cell_size)
            cell_y = int(enemy.pos.y // cell_size)

            neighbors = set()

            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    key = (cell_x + dx, cell_y + dy)

                    if key in grid:
                        neighbors.update(grid[key])

            neighbors.discard(enemy)
            enemy.move_towards(self.player, neighbors)

        if self.player.stats["hp"] <= 0:
            pygame.quit()
            exit()

# ========================== WAVES ================================================
        if self.kills >= self.kills_to_next_wave:
            self.wave += 1
            self.kills = 0

            self.kills_to_next_wave = int(self.kills_to_next_wave * 1.3)

            # spawn mais rápido
            self.spawn_delay = max(200, int(self.spawn_delay * 0.9))

            # 🌊 HORDA
            if self.wave % 5 == 0:
                self.spawn_horde()

            # 👑 BOSS
            if self.wave % 10 == 0:
                self.spawn_boss()

        # tiro
        self.shoot()

        # spawn inimigos
        self.spawn_enemy()

        new_projectiles = []

        for proj in self.projectiles:

            if proj.update(self.enemies):
                new_projectiles.append(proj)

        self.projectiles = new_projectiles

        # ================= COLISÕES =================
        enemies_to_remove = []
        projectiles_to_remove = []

        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                self.player.take_damage(enemy.damage)

        for enemy in self.enemies:
            for proj in self.projectiles:
                if enemy.rect.colliderect(proj.rect):

                    enemy.hp -= proj.damage

                    projectiles_to_remove.append(proj)

                    if enemy.hp <= 0:
                        # 💎 DROP DE XP
                        self.xp_orbs.append(
                            XPOrb(enemy.rect.centerx,
                                  enemy.rect.centery, enemy.xp_value)
                        )

                        self.kills += 1
                        enemies_to_remove.append(enemy)

                        break  # importante

        self.merge_orbs()

   # 🧲 magnetismo
        for orb in self.xp_orbs[:]:
            dx = self.player.pos.x - orb.pos.x
            dy = self.player.pos.y - orb.pos.y

            direction = pygame.Vector2(dx, dy)
            dist = direction.length()

            if dist == 0:
                continue

            direction = direction.normalize()

            magnet_range = self.player.stats["magnet"]

            # 🔹 só ativa dentro do alcance
            if dist < magnet_range:

                # 🔥 aceleração estilo Vampire Survivors
                strength = (1 - (dist / magnet_range))  # 0 → 1
                speed = 2 + (strength ** 2) * 15        # curva suave

                orb.pos += direction * speed
                orb.sync_rect()

            # ⭐ coleta
            if dist < 8:
                gained = int(orb.value * self.player.stats["xp_gain"])

                if self.player.gain_xp(gained):
                    self.start_levelup()

                self.xp_orbs.remove(orb)

                if len(self.xp_orbs) < 50:
                    self.spawn_map_orbs()

        # remover depois (mais seguro)
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)

        for proj in projectiles_to_remove:
            if proj in self.projectiles:
                self.projectiles.remove(proj)

        # ================= LIMPEZA =================
        self.projectiles = [
            p for p in self.projectiles
            if (self.camera_x - 200 < p.rect.x < self.camera_x + settings.WIDTH + 200
                and self.camera_y - 200 < p.rect.y < self.camera_y + settings.HEIGHT + 200)
        ]

    def draw(self, screen):

        if self.state == "menu":
            self.draw_menu(screen)
            pygame.display.flip()
            return

        screen.fill((30, 30, 30))

        # PLAYER
        self.player.draw(screen, self.camera_x, self.camera_y)

        # PROJÉTEIS
        for proj in self.projectiles:
            proj.draw(screen, self.camera_x, self.camera_y)

        # ORBS
        for orb in self.xp_orbs:
            orb.draw(screen, self.camera_x, self.camera_y)

        # INIMIGOS
        for enemy in self.enemies:
            enemy.draw(screen, self.camera_x, self.camera_y)

        # UI (sem câmera)
        self.draw_ui(screen)

        # LEVEL UP (por cima de tudo)
        if self.state == "levelup":
            self.draw_levelup(screen)

        # JANELA DE STATUS
        if self.show_stats:
            self.draw_stats_panel(screen)

        pygame.display.flip()
