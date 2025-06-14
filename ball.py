import pygame

class Ball:
    def __init__(self, x, y, radius, color, dx, dy):
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius
        self.color = color
        self.dx = dx
        self.dy = dy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.radius)

import random

class Ball:
    def __init__(self, x, y, radius, color, dx, dy):
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius
        self.color = color
        self.dx = dx
        self.dy = dy
        self.initial_x = x
        self.initial_y = y

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.radius)

    def move(self, paddles, screen_width, screen_height, scoreboard):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Bounce off top/bottom walls
        if self.rect.top <= 0 or self.rect.bottom >= screen_height:
            self.dy *= -1

        # Bounce off paddles
        for paddle in paddles:
            if self.rect.colliderect(paddle.rect):
                self.dx *= -1
                # Adjust y-velocity based on where the ball hits the paddle
                paddle_center_y = paddle.rect.centery
                ball_center_y = self.rect.centery
                relative_impact = (ball_center_y - paddle_center_y) / (paddle.rect.height / 2)
                self.dy = relative_impact * abs(self.dx if abs(self.dx) > 0 else 5) # Use abs(self.dx) or a default speed if dx is 0
                break # Ensure ball only interacts with one paddle per frame

        # Reset ball if it goes off screen (and update score)
        if self.rect.left <= 0:
            scoreboard.player2_scores()
            self.reset(screen_width, screen_height)
        elif self.rect.right >= screen_width:
            scoreboard.player1_scores()
            self.reset(screen_width, screen_height)

    def reset(self, screen_width, screen_height):
        self.rect.center = (self.initial_x, self.initial_y)
        # Give a random initial y-velocity direction, and x-velocity towards the player who didn't score
        self.dy *= random.choice((1, -1))
        # If player 1 scored (ball went off right), ball moves towards player 2 (left)
        # If player 2 scored (ball went off left), ball moves towards player 1 (right)
        # We can determine this by checking who just scored, or more simply, by checking which side it went off.
        # However, the scoring logic is already in the move method.
        # For simplicity, we'll just make it random or always go to one side first.
        # Let's make it go towards the player who just lost a point.
        if self.dx > 0: # Was moving right, so player 1 scored, ball should go left
            self.dx = -abs(self.dx)
        else: # Was moving left, so player 2 scored, ball should go right
            self.dx = abs(self.dx)

        # Ensure dx is not zero after reset
        if self.dx == 0:
            self.dx = 5 * random.choice((1, -1))
        self.dy = 5 * random.choice((1, -1)) # Reset dy to a fixed initial speed
