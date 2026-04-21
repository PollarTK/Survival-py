import pygame


class XPOrb:
    def __init__(self, x, y, value):
        self.value = value
        self.pos = pygame.Vector2(x, y)

        size = self.get_size()

        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = self.pos

    def get_size(self):
        if self.value > 100:
            return 14
        elif self.value > 35:
            return 10
        elif self.value > 15:
            return 8
        return 6

    def update_visual(self):
        size = self.get_size()

        center = self.pos

        self.rect.width = size
        self.rect.height = size
        self.rect.center = center

    def draw(self, screen, cam_x, cam_y):
        if self.value > 100:
            color = (255, 0, 255)
        elif self.value > 35:
            color = (0, 0, 150)
        elif self.value > 15:
            color = (0, 255, 255)
        else:
            color = (255, 255, 255)

        screen_x = self.pos.x - cam_x
        screen_y = self.pos.y - cam_y

        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)),
                           self.rect.width // 2)
