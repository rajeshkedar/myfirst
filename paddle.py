import pygame

class Paddle:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def move_up(self, speed, screen_height):
        self.rect.y -= speed
        if self.rect.top < 0:
            self.rect.top = 0

    def move_down(self, speed, screen_height):
        self.rect.y += speed
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
