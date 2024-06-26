# Created by Teo Bergkvist as a final project in the course EXTG15 at Lund University 2024.

import pygame
import random
import numpy as np


# Constants
WIDTH, HEIGHT = 640, 480
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 10
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Ball class
class Ball:
    """Class for the pong ball object."""
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.vx = random.choice([-4, 4])
        self.vy = random.choice([-2, 2])

    def move(self):
        """Moves the ball in according to its velocity."""
        self.x += self.vx
        self.y += self.vy

        if self.y <= 0 or self.y >= HEIGHT - BALL_SIZE:
            self.vy = -self.vy


# Paddle class
class Paddle:
    """Class for the pong paddle object."""
    def __init__(self, x, name, nn=None):
        self.nn = nn
        self.name = name
        self.x = x
        self.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.vy = 0

    def move(self):
        """Moves according to its velocity."""
        self.y += self.vy
        self.y = max(min(self.y, HEIGHT - PADDLE_HEIGHT), 0)


# Game class
class Game:
    """Class for the game object."""
    def __init__(self, nn=[None, None], ball_speed_increase=1/20000):
        """Initializes a game object.

        Args:
            nn (list): The neural network objects for the two players. Defaults to [None, None].
        """
        self.ball = Ball()
        self.paddle1 = Paddle(30, "Player 1", nn[0])
        self.paddle2 = Paddle(WIDTH - 30 - PADDLE_WIDTH, "Player 2", nn=nn[1])
        self.winner = None
        self.playtime = 0
        self.ball_speed_increase = ball_speed_increase

    def step(self, action1, action2):
        """Function that lets each paddle take a step.

        Args:
            action1 (float): Value from the action funtion.
            action2 (float): Value from the action funtion.

        Returns:
            paddle object: The paddle that won.
        """
        self.paddle1.vy = action1
        self.paddle2.vy = action2

        self.paddle1.move()
        self.paddle2.move()
        self.ball.move()
        self.playtime += 1

        # Collision with paddles
        if (
            self.paddle1.x < self.ball.x < self.paddle1.x + PADDLE_WIDTH
            and self.paddle1.y < self.ball.y < self.paddle1.y + PADDLE_HEIGHT
        ):
            self.ball.vx = -self.ball.vx + (self.ball_speed_increase * self.playtime)
        if (
            self.paddle2.x < self.ball.x + BALL_SIZE < self.paddle2.x + PADDLE_WIDTH
            and self.paddle2.y < self.ball.y < self.paddle2.y + PADDLE_HEIGHT
        ):
            self.ball.vx = -self.ball.vx + (self.ball_speed_increase * self.playtime)

        # Check for ball going out of bounds
        if self.ball.x <= 0:
            self.winner = self.paddle2
        elif self.ball.x >= WIDTH - BALL_SIZE:
            self.winner = self.paddle1

        return self.winner


# Neural network action function
def get_action(ball, paddle, opponent):
    """Function to calculate an action with the neural nets.

    Args:
        ball (ball object): Needed for its coordinates.
        paddle (paddle object): The paddle object with its neural network.
        opponent (paddle object): The opponents paddle object, needed for its coordinates.

    Returns:
        float: The direction to move.
    """
    state = np.array([ball.x, ball.y, paddle.y, opponent.y])
    if paddle.nn is None:
        action = random.choice([-5, 0, 5])
    else:
        action = paddle.nn.predict(state)
    return action


def create_game_matrix(players):
    """A function to create the matrix containing all possible game combinations.

    Args:
        players (list): List of all players.

    Returns:
        _type_: A nxn array, with all possible game combinations.
    """
    number_of_players = len(players)
    game_matrix = np.empty((number_of_players, number_of_players), dtype=Game)
    for row in range(number_of_players):
        for col in range(number_of_players):
            if row == col:
                continue
            if game_matrix[col][row] is None:
                nn = [players[row][1], players[col][1]]
                game_matrix[row][col] = Game(nn)
    return game_matrix


# GUI Simulation.
def run_pygame(game):
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        action1 = get_action(game.ball, game.paddle1, game.paddle2)
        action2 = get_action(game.ball, game.paddle2, game.paddle1)

        winner = game.step(action1, action2)
        if winner:
            print(f"{winner.name} wins!")
            running = False

        screen.fill(BLACK)
        pygame.draw.rect(
            screen, WHITE, (game.paddle1.x, game.paddle1.y, PADDLE_WIDTH, PADDLE_HEIGHT)
        )
        pygame.draw.rect(
            screen, WHITE, (game.paddle2.x, game.paddle2.y, PADDLE_WIDTH, PADDLE_HEIGHT)
        )
        pygame.draw.rect(
            screen, WHITE, (game.ball.x, game.ball.y, BALL_SIZE, BALL_SIZE)
        )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


# Headless simulation function
def run_headless(game, verbose=False):
    winner = None
    while not game.winner:
        action1 = get_action(game.ball, game.paddle1, game.paddle2)
        action2 = get_action(game.ball, game.paddle2, game.paddle1)
        winner = game.step(action1, action2)
    if verbose:
        print(f"Player {winner.name} wins!")
    return winner
