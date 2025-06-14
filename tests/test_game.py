import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Temporarily mock pygame modules for headless testing if full pygame is not needed
# This is tricky because main.py's Game class calls pygame.init(), display.set_mode() etc.
# For logic tests, we might not need a real screen.
# We'll need to patch specific pygame functions used in Game methods if they cause issues.

# Assuming pygame is installed (as per previous test files), we won't do a global mock here.
# Targeted patching will be used in setUp for problematic pygame calls.
import pygame # Import pygame for its constants like KEYDOWN, K_p

from main import Game, WINNING_SCORE, SCREEN_WIDTH, SCREEN_HEIGHT, INITIAL_BALL_SPEED_X, INITIAL_BALL_SPEED_Y
# from ball import Ball # Not strictly needed for these tests if we trust ball interactions
# from paddle import Paddle # Not strictly needed
from scoreboard import Scoreboard


class TestGame(unittest.TestCase):

    def setUp(self):
        # If not MOCK_PYGAME, this will use real pygame, which might require a display.
        # The Game class calls pygame.init() and sets up a screen.
        # We can patch specific methods if they are problematic in a headless environment.

        # Patch methods that might cause issues in headless (display, events)
        # We are testing game logic, not rendering or event polling here.
        patcher_display_set_mode = patch('pygame.display.set_mode', MagicMock(return_value=MagicMock()))
        patcher_display_set_caption = patch('pygame.display.set_caption', MagicMock())
        patcher_display_flip = patch('pygame.display.flip', MagicMock())
        patcher_event_get = patch('pygame.event.get', MagicMock(return_value=[])) # No events
        patcher_font_Font = patch('pygame.font.Font', MagicMock(return_value=MagicMock(render=MagicMock(return_value=MagicMock(get_rect=MagicMock(return_value=MagicMock(x=0,y=0,width=0,height=0,center=(0,0))))))))


        self.mock_set_mode = patcher_display_set_mode.start()
        self.addCleanup(patcher_display_set_mode.stop)
        self.mock_set_caption = patcher_display_set_caption.start()
        self.addCleanup(patcher_display_set_caption.stop)
        self.mock_flip = patcher_display_flip.start()
        self.addCleanup(patcher_display_flip.stop)
        self.mock_event_get = patcher_event_get.start()
        self.addCleanup(patcher_event_get.stop)
        self.mock_font_Font = patcher_font_Font.start()
        self.addCleanup(patcher_font_Font.stop)


        self.game = Game()
        # Ensure game starts in a predictable state for tests if needed
        self.game.game_state = "playing"
        self.game.match_over = False
        self.game.game_paused = False
        self.game.scoreboard.reset_scores()


    def test_initial_state(self):
        self.assertEqual(self.game.scoreboard.player1_score, 0)
        self.assertEqual(self.game.scoreboard.player2_score, 0)
        self.assertFalse(self.game.match_over)
        self.assertEqual(self.game.game_state, "playing")

    def test_scoring_player1(self):
        # Player 1 scores when ball goes off right edge
        self.game.ball.rect.right = SCREEN_WIDTH + 10 # Move ball off right edge
        self.game.ball.dx = INITIAL_BALL_SPEED_X # Ensure it's moving right

        # update_game_state calls ball.move, which should handle scoring & reset
        with patch('main.random.choice', lambda x: x[0]): # Mock random for predictable ball reset
            self.game.update_game_state()

        self.assertEqual(self.game.scoreboard.player1_score, 1)
        self.assertEqual(self.game.scoreboard.player2_score, 0)
        # Ball should be reset to center
        self.assertEqual(self.game.ball.rect.centerx, SCREEN_WIDTH // 2)
        self.assertEqual(self.game.ball.rect.centery, SCREEN_HEIGHT // 2)

    def test_scoring_player2(self):
        # Player 2 scores when ball goes off left edge
        self.game.ball.rect.left = -10 # Move ball off left edge
        self.game.ball.dx = -INITIAL_BALL_SPEED_X # Ensure it's moving left

        with patch('main.random.choice', lambda x: x[0]): # Mock random for predictable ball reset
             self.game.update_game_state()

        self.assertEqual(self.game.scoreboard.player2_score, 1)
        self.assertEqual(self.game.scoreboard.player1_score, 0)
        self.assertEqual(self.game.ball.rect.centerx, SCREEN_WIDTH // 2)

    def test_game_ending_condition_player1_wins(self):
        self.game.scoreboard.player1_score = WINNING_SCORE - 1
        self.game.scoreboard.player2_score = 0

        # Simulate player 1 scoring the winning point
        self.game.ball.rect.right = SCREEN_WIDTH + 10
        self.game.ball.dx = INITIAL_BALL_SPEED_X

        with patch('main.random.choice', lambda x: x[0]):
            self.game.update_game_state()

        self.assertEqual(self.game.scoreboard.player1_score, WINNING_SCORE)
        self.assertTrue(self.game.match_over)
        self.assertEqual(self.game.winner_text, "Player 1 Wins!")

    def test_game_ending_condition_player2_wins(self):
        self.game.scoreboard.player1_score = 0
        self.game.scoreboard.player2_score = WINNING_SCORE - 1

        self.game.ball.rect.left = -10
        self.game.ball.dx = -INITIAL_BALL_SPEED_X

        with patch('main.random.choice', lambda x: x[0]):
            self.game.update_game_state()

        self.assertEqual(self.game.scoreboard.player2_score, WINNING_SCORE)
        self.assertTrue(self.game.match_over)
        self.assertEqual(self.game.winner_text, "Player 2 Wins!")

    def test_reset_match_after_game_over(self):
        # Setup game over state
        self.game.scoreboard.player1_score = WINNING_SCORE
        self.game.match_over = True
        self.game.winner_text = "Player 1 Wins!"

        # Call reset_match (or simulate 'R' key press that calls it)
        self.game.reset_match()

        self.assertEqual(self.game.scoreboard.player1_score, 0)
        self.assertEqual(self.game.scoreboard.player2_score, 0)
        self.assertFalse(self.game.match_over)
        self.assertEqual(self.game.winner_text, "")
        # Ball should be reset
        self.assertEqual(self.game.ball.rect.centerx, SCREEN_WIDTH // 2)
        # Paddles should be reset
        self.assertEqual(self.game.player1_paddle.rect.centery, SCREEN_HEIGHT // 2)


    def test_pause_functionality(self):
        self.game.game_state = "playing"
        self.assertFalse(self.game.game_paused)

        # Simulate pressing 'P' to pause
        # We need to mock pygame.event.get() to return a P key press event
        mock_p_down_event = MagicMock()
        mock_p_down_event.type = pygame.KEYDOWN
        mock_p_down_event.key = pygame.K_p

        # Ensure event.get is the one from setUp, or re-patch if needed for this specific event
        self.mock_event_get.return_value = [mock_p_down_event]
        self.game.handle_input() # Process the event
        self.assertTrue(self.game.game_paused)

        # Simulate pressing 'P' again to unpause
        self.mock_event_get.return_value = [mock_p_down_event] # Same event again
        self.game.handle_input() # Process the event
        self.assertFalse(self.game.game_paused)


if __name__ == '__main__':
    # This allows running this test file directly.
    # Game() class now handles pygame.init().
    unittest.main()
