import pygame

import pygame
import random

# Screen dimensions and constants (can remain module-level)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Simple Pygame Example"
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_COLOR = LIGHT_GRAY
PADDLE_SPEED = 7
AI_PADDLE_SPEED = PADDLE_SPEED * 0.85

BALL_RADIUS = 10
BALL_COLOR = LIGHT_GRAY
INITIAL_BALL_SPEED_X = 5
INITIAL_BALL_SPEED_Y = 5

WINNING_SCORE = 10

# Import classes
from paddle import Paddle
from ball import Ball
from scoreboard import Scoreboard

class Game:
    def __init__(self):
        pygame.init() # Initialize Pygame here
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        self.clock = pygame.time.Clock()

        self.player1_paddle = Paddle(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLOR)
        self.player2_paddle = Paddle(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLOR)
        self.paddles = [self.player1_paddle, self.player2_paddle]

        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_RADIUS, BALL_COLOR,
                         INITIAL_BALL_SPEED_X * random.choice((1,-1)),
                         INITIAL_BALL_SPEED_Y * random.choice((1,-1)))

        self.scoreboard = Scoreboard(SCREEN_WIDTH, font_size=40, color=LIGHT_GRAY)

        self.game_state = "start_screen"  # "start_screen", "playing"
        self.game_paused = False
        self.game_mode = "AI"  # Default, can be changed by "start screen"
        self.round_over = False # True when a player scores, reset when round restarts (ball reset)
        self.match_over = False # True when a player reaches WINNING_SCORE
        self.winner_text = ""

        self.font_cache = {} # Cache fonts for draw_text

    def _get_font(self, size):
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.Font(None, size)
        return self.font_cache[size]

    def draw_text(self, text, font_size, color, center_pos):
        font = self._get_font(font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center_pos)
        self.screen.blit(text_surface, text_rect)

    def draw_center_line(self):
        for i in range(0, SCREEN_HEIGHT, 25):
            pygame.draw.rect(self.screen, LIGHT_GRAY, (SCREEN_WIDTH // 2 - 2, i, 4, 15))

    def reset_round(self):
        """Resets ball and paddle positions for a new round, keeps scores."""
        self.player1_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.player2_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.ball.reset(SCREEN_WIDTH, SCREEN_HEIGHT) # Resets ball position and velocity
        self.round_over = False # Not strictly used here as ball.move handles scoring and reset

    def reset_match(self):
        """Resets scores, round, and match status for a completely new match."""
        self.scoreboard.reset_scores()
        self.reset_round() # Reset paddles and ball
        self.match_over = False
        self.winner_text = ""
        # self.game_state = "playing" # Or could go to start_screen if called from there

    def start_new_match(self, selected_mode):
        """Sets up a new match with the chosen mode."""
        self.reset_match()
        self.game_mode = selected_mode
        self.game_state = "playing"

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False # Signal to quit

            if self.game_state == "start_screen":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.start_new_match("AI")
                    elif event.key == pygame.K_2:
                        self.start_new_match("2P")
            elif self.game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if self.match_over:
                        if event.key == pygame.K_r:
                            self.reset_match() # Reset the whole match
                        elif event.key == pygame.K_m:
                            self.game_state = "start_screen"
                            self.match_over = False # Ensure these are reset for clean start screen
                            self.winner_text = ""
                    elif not self.game_paused and event.key == pygame.K_p: # Pause only if not match_over
                         self.game_paused = True
                    elif self.game_paused and event.key == pygame.K_p: # Unpause
                         self.game_paused = False

        if self.game_state == "playing" and not self.match_over and not self.game_paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: # Corrected: removed duplicate if
                self.player1_paddle.move_up(PADDLE_SPEED, SCREEN_HEIGHT)
            if keys[pygame.K_s]:
                self.player1_paddle.move_down(PADDLE_SPEED, SCREEN_HEIGHT)

            if self.game_mode == "2P":
                if keys[pygame.K_UP]:
                    self.player2_paddle.move_up(PADDLE_SPEED, SCREEN_HEIGHT)
                if keys[pygame.K_DOWN]:
                    self.player2_paddle.move_down(PADDLE_SPEED, SCREEN_HEIGHT)
        return True # Signal to continue running

    def update_game_state(self):
        if self.game_state == "playing" and not self.match_over and not self.game_paused:
            # AI movement
            if self.game_mode == "AI":
                if self.player2_paddle.rect.centery < self.ball.rect.centery:
                    self.player2_paddle.move_down(AI_PADDLE_SPEED, SCREEN_HEIGHT)
                if self.player2_paddle.rect.centery > self.ball.rect.centery:
                    self.player2_paddle.move_up(AI_PADDLE_SPEED, SCREEN_HEIGHT)

            # Ball movement and scoring (ball.move updates scoreboard internally)
            # Ball.move will also call ball.reset if it goes off screen.
            # Ball.reset in turn resets its own position and velocity.
            self.ball.move(self.paddles, SCREEN_WIDTH, SCREEN_HEIGHT, self.scoreboard)

            # Check for match over condition
            if self.scoreboard.player1_score >= WINNING_SCORE:
                self.winner_text = "Player 1 Wins!"
                self.match_over = True
            elif self.scoreboard.player2_score >= WINNING_SCORE:
                self.winner_text = "Player 2 Wins!"
                self.match_over = True

    def draw_elements(self):
        self.screen.fill(DARK_GRAY)

        if self.game_state == "start_screen":
            self.draw_text("PONG", 74, LIGHT_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
            self.draw_text("Press 1 for Single Player (vs AI)", 30, LIGHT_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            self.draw_text("Press 2 for Two Players", 30, LIGHT_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            self.draw_text("W/S for P1, UP/DOWN for P2 (if 2P)", 24, LIGHT_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.draw_text("P to Pause, R to Reset Match, M for Menu", 24, LIGHT_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))

        elif self.game_state == "playing":
            self.draw_center_line()
            self.player1_paddle.draw(self.screen)
            self.player2_paddle.draw(self.screen)
            self.ball.draw(self.screen)
            self.scoreboard.draw(self.screen)

            if self.match_over:
                self.draw_text("Match Over", 74, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                self.draw_text(self.winner_text, 50, LIGHT_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
                self.draw_text("Press 'R' to Reset Match", 30, LIGHT_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
                self.draw_text("Press 'M' for Main Menu", 30, LIGHT_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
            elif self.game_paused:
                self.draw_text("Paused", 74, LIGHT_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.draw_text("Press P to Resume", 30, LIGHT_GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            if not running:
                break

            self.update_game_state()
            self.draw_elements()
            self.clock.tick(60)

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
