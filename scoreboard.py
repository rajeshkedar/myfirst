import pygame

class Scoreboard:
    def __init__(self, screen_width, font_size=30, color=(0, 0, 0)):
        self.player1_score = 0
        self.player2_score = 0
        self.font = pygame.font.Font(None, font_size)
        self.color = color
        self.screen_width = screen_width
        self.y_position = 20  # Position from the top

    def draw(self, screen):
        score_text = f"{self.player1_score} - {self.player2_score}"
        text_surface = self.font.render(score_text, True, self.color)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.y_position))
        screen.blit(text_surface, text_rect)

    def player1_scores(self):
        self.player1_score += 1

    def player2_scores(self):
        self.player2_score += 1

    def reset_scores(self):
        self.player1_score = 0
        self.player2_score = 0
