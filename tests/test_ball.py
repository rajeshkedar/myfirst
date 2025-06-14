import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the Python path to allow module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ball import Ball
# Need to mock pygame.Rect for headless testing if it's not available
try:
    import pygame
    Rect = pygame.Rect
except ImportError:
    # Minimal mock Rect if pygame is not available (e.g., in a CI environment without display)
    class Rect:
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.left = x
            self.right = x + width
            self.top = y
            self.bottom = y + height
            self.center = (x + width // 2, y + height // 2)
            self.centery = y + height // 2

        def colliderect(self, other_rect):
            # Simple collision detection
            return not (self.right < other_rect.left or
                        self.left > other_rect.right or
                        self.bottom < other_rect.top or
                        self.top > other_rect.bottom)

    # If pygame is mocked, Ball.rect will use this.
    # We might need to ensure Ball class uses this Rect too.
    # One way is to patch 'pygame.Rect' in the ball module during tests.
    # For now, let's assume Ball can be instantiated and its self.rect will behave as expected.
    # If Ball internally calls pygame.Rect, that would need patching.
    # ball.py: self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
    # So, we will patch 'ball.pygame.Rect'

# Mock Paddle class
class MockPaddle:
    def __init__(self, x, y, width, height):
        self.rect = Rect(x, y, width, height)
        self.height = height # Ball uses paddle.rect.height

# Mock Scoreboard class
class MockScoreboard:
    def __init__(self):
        self.player1_score = 0
        self.player2_score = 0

    def player1_scores(self):
        self.player1_score += 1

    def player2_scores(self):
        self.player2_score += 1

    def reset_scores(self):
        self.player1_score = 0
        self.player2_score = 0

class TestBall(unittest.TestCase):
    # Class-level patcher for pygame.Rect in the ball module
    # This ensures that Ball.__init__ uses the (potentially mocked) Rect
    rect_patcher = patch('ball.pygame.Rect', Rect)

    def setUp(self):
        # Start the patcher and keep a reference to the mock object it returns (our Rect class/mock)
        self.PatchedRect = TestBall.rect_patcher.start()
        self.addCleanup(TestBall.rect_patcher.stop) # Ensure the patch is stopped after each test

        self.screen_width = 800
        self.screen_height = 600
        self.ball_radius = 10

        # Now, when Ball() is called, it will use self.PatchedRect for pygame.Rect
        self.ball = Ball(
            x=self.screen_width // 2,
            y=self.screen_height // 2,
            radius=self.ball_radius,
            color=(255, 255, 255),
            dx=5,
            dy=5
        )
        self.mock_scoreboard = MockScoreboard()
        # Our MockPaddle uses the global Rect (which could be pygame.Rect or our mock if pygame isn't installed)
        # This is fine as long as it's consistent.
        self.paddle1 = MockPaddle(50, self.screen_height // 2 - 50, 10, 100)
        self.paddle2 = MockPaddle(self.screen_width - 60, self.screen_height // 2 - 50, 10, 100)
        self.paddles = [self.paddle1, self.paddle2]

    def test_ball_creation(self):
        # Test that the ball is created at the center of its rect
        self.assertEqual(self.ball.rect.center, (self.screen_width // 2, self.screen_height // 2))
        self.assertEqual(self.ball.dx, 5)
        self.assertEqual(self.ball.dy, 5)
        # Check that the rect of the ball is an instance of our PatchedRect
        self.assertTrue(isinstance(self.ball.rect, self.PatchedRect))

    def test_ball_movement(self):
        initial_x = self.ball.rect.x
        initial_y = self.ball.rect.y
        self.ball.move(self.paddles, self.screen_width, self.screen_height, self.mock_scoreboard)
        self.assertEqual(self.ball.rect.x, initial_x + self.ball.dx)
        self.assertEqual(self.ball.rect.y, initial_y + self.ball.dy)

    def test_bounce_top_wall(self):
        self.ball.rect.top = 0
        self.ball.dy = -5 # Moving upwards
        self.ball.move(self.paddles, self.screen_width, self.screen_height, self.mock_scoreboard)
        self.assertEqual(self.ball.dy, 5) # Should reverse dy

    def test_bounce_bottom_wall(self):
        self.ball.rect.bottom = self.screen_height
        self.ball.dy = 5 # Moving downwards
        self.ball.move(self.paddles, self.screen_width, self.screen_height, self.mock_scoreboard)
        self.assertEqual(self.ball.dy, -5) # Should reverse dy

    def test_bounce_paddle1(self):
        self.ball.rect.left = self.paddle1.rect.right - 1
        # Set ball.dy to 0 so that its y position doesn't change before collision calculation
        self.ball.dy = 0
        self.ball.rect.centery = self.paddle1.rect.centery
        self.ball.dx = -5
        self.ball.move([self.paddle1], self.screen_width, self.screen_height, self.mock_scoreboard)
        self.assertEqual(self.ball.dx, 5)
        self.assertAlmostEqual(self.ball.dy, 0)

    def test_bounce_paddle2_top_edge(self):
        # Set ball.dy to 0 to simplify y-positioning for collision point
        self.ball.dy = 0
        self.ball.rect.right = self.paddle2.rect.left + 1
        self.ball.rect.centery = self.paddle2.rect.top + (self.paddle2.rect.height * 0.1)
        self.ball.dx = 5
        self.ball.move([self.paddle2], self.screen_width, self.screen_height, self.mock_scoreboard)
        self.assertEqual(self.ball.dx, -5)
        self.assertTrue(self.ball.dy < 0)

    # Method decorator for random.choice
    # The mock object for random.choice is passed as the first argument after self
    @patch('ball.random.choice')
    def test_reset_ball_goes_off_left(self, mock_rand_choice_method_arg):
        mock_rand_choice_method_arg.return_value = 1 # Configure mock return value
        self.ball.rect.left = -1
        initial_dx = self.ball.dx = -5
        self.ball.move(self.paddles, self.screen_width, self.screen_height, self.mock_scoreboard)
        self.assertEqual(self.mock_scoreboard.player2_score, 1)
        self.assertEqual(self.ball.rect.center, (self.ball.initial_x, self.ball.initial_y))
        self.assertEqual(self.ball.dx, abs(initial_dx))
        self.assertEqual(self.ball.dy, 5 * 1)
        # random.choice is called multiple times in reset, so assert_called_once_with is too strict.
        # We care that it was called, and our mock controlled the outcome for the final dy assignment.
        self.assertTrue(mock_rand_choice_method_arg.called)

    @patch('ball.random.choice')
    def test_reset_ball_goes_off_right(self, mock_rand_choice_method_arg):
        mock_rand_choice_method_arg.return_value = -1 # Configure mock return value
        self.ball.rect.right = self.screen_width + 1
        initial_dx = self.ball.dx = 5
        self.ball.move(self.paddles, self.screen_width, self.screen_height, self.mock_scoreboard)
        self.assertEqual(self.mock_scoreboard.player1_score, 1)
        self.assertEqual(self.ball.rect.center, (self.ball.initial_x, self.ball.initial_y))
        self.assertEqual(self.ball.dx, -abs(initial_dx))
        self.assertEqual(self.ball.dy, 5 * (-1))
        # random.choice is called multiple times in reset.
        self.assertTrue(mock_rand_choice_method_arg.called)

    def test_ball_paddle_collision_dy_adjustment(self):
        self.paddle1.rect.y = self.screen_height // 2 - 50
        self.ball.rect.left = self.paddle1.rect.right - 1
        self.ball.rect.centery = self.paddle1.rect.top
        self.ball.dx = -5
        self.ball.dy = 0
        self.ball.move([self.paddle1], self.screen_width, self.screen_height, self.mock_scoreboard)
        self.assertEqual(self.ball.dx, 5)
        expected_dy = -1 * abs(self.ball.dx)
        self.assertAlmostEqual(self.ball.dy, expected_dy)

        self.ball.rect.left = self.paddle1.rect.right - 1
        self.ball.rect.centery = self.paddle1.rect.bottom
        self.ball.dx = -5
        self.ball.dy = 0
        self.ball.move([self.paddle1], self.screen_width, self.screen_height, self.mock_scoreboard)
        self.assertEqual(self.ball.dx, 5)
        expected_dy = 1 * abs(self.ball.dx)
        self.assertAlmostEqual(self.ball.dy, expected_dy)

if __name__ == '__main__':
    unittest.main()
