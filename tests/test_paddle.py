import unittest
from unittest.mock import patch
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paddle import Paddle

# Use the same mock Rect as in test_ball.py if pygame is not available
try:
    import pygame
    Rect = pygame.Rect
except ImportError:
    class Rect:
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.top = y
            self.bottom = y + height
            self.left = x
            self.right = x + width
            # Add other attributes if Paddle uses them (e.g., centery)
            self.centery = y + height // 2
            self.centerx = x + width // 2 # Though paddle doesn't use this for movement

        # Paddle's move methods directly manipulate self.rect.y, self.rect.top, self.rect.bottom
        # No complex Rect methods seem to be called by Paddle itself beyond attribute access.

class TestPaddle(unittest.TestCase):

    rect_patcher = patch('paddle.pygame.Rect', Rect) # Patch Rect in paddle.py

    def setUp(self):
        self.PatchedRect = TestPaddle.rect_patcher.start()
        self.addCleanup(TestPaddle.rect_patcher.stop)

        self.screen_height = 600
        self.paddle_width = 10
        self.paddle_height = 100
        self.initial_x = 50
        self.initial_y = self.screen_height // 2 - self.paddle_height // 2

        self.paddle = Paddle(
            x=self.initial_x,
            y=self.initial_y,
            width=self.paddle_width,
            height=self.paddle_height,
            color=(255, 255, 255)
        )
        self.move_speed = 5

    def test_paddle_creation(self):
        self.assertEqual(self.paddle.rect.x, self.initial_x)
        self.assertEqual(self.paddle.rect.y, self.initial_y)
        self.assertEqual(self.paddle.rect.width, self.paddle_width)
        self.assertEqual(self.paddle.rect.height, self.paddle_height)
        self.assertTrue(isinstance(self.paddle.rect, self.PatchedRect))

    def test_move_up(self):
        initial_y = self.paddle.rect.y
        self.paddle.move_up(self.move_speed, self.screen_height)
        self.assertEqual(self.paddle.rect.y, initial_y - self.move_speed)

    def test_move_up_boundary(self):
        # Move paddle to the top edge
        self.paddle.rect.y = 0
        # Try to move further up
        self.paddle.move_up(self.move_speed, self.screen_height)
        # y should remain 0 (or rect.top should be 0)
        self.assertEqual(self.paddle.rect.top, 0)
        self.assertEqual(self.paddle.rect.y, 0)


    def test_move_up_past_boundary(self):
        # Position paddle such that a normal move would go past boundary
        self.paddle.rect.y = self.move_speed - 1 # e.g., y=4, speed=5
        self.paddle.move_up(self.move_speed, self.screen_height)
        self.assertEqual(self.paddle.rect.top, 0) # Should be clamped to 0
        self.assertEqual(self.paddle.rect.y, 0)


    def test_move_down(self):
        initial_y = self.paddle.rect.y
        self.paddle.move_down(self.move_speed, self.screen_height)
        self.assertEqual(self.paddle.rect.y, initial_y + self.move_speed)

    def test_move_down_boundary(self):
        # Move paddle to the bottom edge
        self.paddle.rect.bottom = self.screen_height
        # Ensure y is consistent with bottom
        self.paddle.rect.y = self.screen_height - self.paddle_height

        # Try to move further down
        self.paddle.move_down(self.move_speed, self.screen_height)

        # rect.bottom should remain screen_height
        self.assertEqual(self.paddle.rect.bottom, self.screen_height)
        self.assertEqual(self.paddle.rect.y, self.screen_height - self.paddle_height)


    def test_move_down_past_boundary(self):
        # Position paddle such that a normal move would go past boundary
        # rect.bottom = current_y + height
        # target_bottom = current_y + height + speed
        # We want target_bottom > screen_height
        # current_y + height + speed > screen_height
        # current_y > screen_height - height - speed
        # Let current_y = screen_height - height - speed + 1
        self.paddle.rect.y = (self.screen_height - self.paddle_height - self.move_speed) + 1

        self.paddle.move_down(self.move_speed, self.screen_height)

        self.assertEqual(self.paddle.rect.bottom, self.screen_height)
        self.assertEqual(self.paddle.rect.y, self.screen_height - self.paddle_height)

if __name__ == '__main__':
    unittest.main()
