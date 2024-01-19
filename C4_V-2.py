import pygame
import sys
import math

# Pygame setup
pygame.init()
WIDTH = 700
HEIGHT = 750
ROWS = 6  # Updated to 6 rows
COLS = 7
SQUARESIZE = WIDTH // COLS

# RGB colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Connect 4')

font = pygame.font.SysFont('comicsans', 40)
large_font = pygame.font.SysFont('comicsans', 80)
button_font = pygame.font.SysFont(None, 24)
BUTTON_COLOR = (100, 100, 100)
EXIT_BUTTON_COLOR = (255, 0, 0)  # Red
button_text_color = (0, 0, 0)  # Black

class Game:

    def __init__(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.turn = 0
        self.game_over = False
        self.ai_algorithm = "Minimax"  # Default AI algorithm

    # Place piece on board
    def drop_piece(self, col, player):
        row = self.get_next_open_row(col)
        if row is not None:
            self.board[row][col] = player
            return True
        return False

    # Get next open row
    def get_next_open_row(self, col):
        if col < 0 or col >= COLS:
            return None
        for r in range(ROWS):
            if self.board[r][col] == 0:
                return r
        return None  # Return None if the column is already filled


    # Evaluate the current state of the board
    def evaluate_board(self):
        score = 0
        # Evaluate vertical wins
        for c in range(COLS):
            for r in range(ROWS - 3):
                window = [self.board[r+i][c] for i in range(4)]
                score += self.evaluate_window(window)
        # Evaluate horizontal wins
        for r in range(ROWS):
            for c in range(COLS - 3):
                window = [self.board[r][c+i] for i in range(4)]
                score += self.evaluate_window(window)
        # Evaluate diagonal (right-down) wins
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [self.board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window)
        # Evaluate diagonal (left-down) wins
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [self.board[r+i][c+3-i] for i in range(4)]
                score += self.evaluate_window(window)
        return score

    # Evaluate a window of 4 pieces
    def evaluate_window(self, window):
        score = 0
        player = self.turn + 1

        if window.count(player) == 4:
            score += 100
        elif window.count(player) == 3 and window.count(0) == 1:
            score += 5
        elif window.count(player) == 2 and window.count(0) == 2:
            score += 2

        opponent = 3 - player  # Assuming there are only two players (1 and 2)
        if window.count(opponent) == 3 and window.count(0) == 1:
            score -= 4

        return score

    # Minimax algorithm
    def minimax(self, depth, alpha, beta, maximizingPlayer, valid_moves):
        if depth == 0 or self.check_win(1) or self.check_win(2) or self.check_tie():
            return self.evaluate_board()

        if maximizingPlayer:
            max_eval = -math.inf
            for col in valid_moves:
                row = self.get_next_open_row(col)
                self.board[row][col] = 1  # Assume the AI (player 1) makes the move
                eval = self.minimax(depth - 1, alpha, beta, False, valid_moves)
                self.board[row][col] = 0
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for col in valid_moves:
                row = self.get_next_open_row(col)
                self.board[row][col] = 2  # Assume the opponent (player 2) makes the move
                eval = self.minimax(depth - 1, alpha, beta, True, valid_moves)
                self.board[row][col] = 0
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval


    
    # Alpha-beta pruning
    def alphabeta(self, depth, alpha, beta, maximizingPlayer, valid_moves):
        if depth == 0 or self.check_win(1) or self.check_win(2) or self.check_tie():
            return self.evaluate_board()

        if maximizingPlayer:
            max_eval = -math.inf
            for col in valid_moves:
                row = self.get_next_open_row(col)
                self.board[row][col] = 1  # Assume the AI (player 1) makes the move
                eval = self.alphabeta(depth - 1, alpha, beta, False, valid_moves)
                self.board[row][col] = 0
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for col in valid_moves:
                row = self.get_next_open_row(col)
                self.board[row][col] = 2  # Assume the opponent (player 2) makes the move
                eval = self.alphabeta(depth - 1, alpha, beta, True, valid_moves)
                self.board[row][col] = 0
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval


    # Check if a location is valid for a move
    def is_valid_location(self, col):
        return self.board[ROWS - 1][col] == 0

    # Make the AI's move
    def make_ai_move(self, algorithm=None):
        if algorithm is not None:
            self.ai_algorithm = algorithm

        if self.turn == 1 and not self.game_over:
            valid_moves = [col for col in range(COLS) if self.is_valid_location(col)]
            if valid_moves:
                if self.ai_algorithm == "Minimax":
                    best_col = self.minimax(4, -math.inf, math.inf, True, valid_moves)
                else:
                    best_col = self.alphabeta(4, -math.inf, math.inf, True, valid_moves)

                if self.drop_piece(best_col, player=1):  # Make the best move
                    self.turn = 0  # Switch to player 2's turn
                    if self.check_win(1):  # Check if the AI (player 1) wins
                        self.show_gameover(1)
                        self.game_over = True

        self.draw()
        pygame.display.update()

    # Check horizontal win
    def check_horizontal(self, piece):
        for r in range(ROWS):
            for c in range(COLS - 3):
                if self.board[r][c] == piece and self.board[r][c + 1] == piece and self.board[r][c + 2] == piece and self.board[r][c + 3] == piece:
                    return True
        return False

    # Check vertical win
    def check_vertical(self, piece):
        for c in range(COLS):
            for r in range(ROWS - 3):
                if self.board[r][c] == piece and self.board[r + 1][c] == piece and self.board[r + 2][c] == piece and self.board[r + 3][c] == piece:
                    return True
        return False

    # Check diagonal win
    def check_diagonal(self, piece):
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if self.board[r][c] == piece and self.board[r + 1][c + 1] == piece and self.board[r + 2][c + 2] == piece and self.board[r + 3][c + 3] == piece:
                    return True

        for r in range(ROWS - 3):
            for c in range(3, COLS):
                if self.board[r][c] == piece and self.board[r + 1][c - 1] == piece and self.board[r + 2][c - 2] == piece and self.board[r + 3][c - 3] == piece:
                    return True
        return False

    # Check for win
    def check_win(self, piece):
        return self.check_vertical(piece) or self.check_horizontal(piece) or self.check_diagonal(piece)

    # Check for tie
    def check_tie(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c] == 0:
                    return False
        return True

    # Draw board and pieces
    def draw(self):
        vertical_offset = HEIGHT - (SQUARESIZE * ROWS)
        for r in range(ROWS):
            for c in range(COLS):
                pygame.draw.rect(screen, BLACK, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE + vertical_offset, SQUARESIZE, SQUARESIZE))
                if self.board[r][c] == 1:
                    pygame.draw.circle(screen, RED, (c * SQUARESIZE + SQUARESIZE // 2, r * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2 + vertical_offset), SQUARESIZE // 2 - 5)
                elif self.board[r][c] == 2:
                    pygame.draw.circle(screen, YELLOW, (c * SQUARESIZE + SQUARESIZE // 2, r * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2 + vertical_offset), SQUARESIZE // 2 - 5)

        # Handle button display
        self.handle_buttons()

        pygame.display.update()

    # Show game over
    def show_gameover(self, winner):
        pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 100))
        text = large_font.render("Player " + str(winner) + " Wins!", True, YELLOW)
        screen.blit(text, (WIDTH // 2 - 95, HEIGHT // 2 + 20))
        pygame.display.update()

    def handle_buttons(self):
        # Define button dimensions and positions
        button_width = 100
        button_height = 40
        button_x = 10
        button_y = 10
        button_margin = 10

        # Button text
        minimax_text = button_font.render("Minimax", True, button_text_color)
        alphabeta_text = button_font.render("Alpha-Beta", True, button_text_color)
        new_text = button_font.render("New", True, button_text_color)
        restart_text = button_font.render("Restart", True, button_text_color)
        exit_text = button_font.render("Exit", True, button_text_color)

        # Create buttons
        minimax_button = pygame.Rect(button_x, button_y, button_width, button_height)
        alphabeta_button = pygame.Rect(button_x + button_width + button_margin, button_y, button_width, button_height)
        new_button = pygame.Rect(WIDTH - 3 * button_width - 30, button_y, button_width, button_height)
        restart_button = pygame.Rect(WIDTH - 2 * button_width - 20, button_y, button_width, button_height)
        exit_button = pygame.Rect(WIDTH - button_width - 10, button_y, button_width, button_height)

        # Draw buttons and text
        pygame.draw.rect(screen, BUTTON_COLOR, minimax_button)
        screen.blit(minimax_text, (minimax_button.x + 18, minimax_button.y + 10))

        pygame.draw.rect(screen, BUTTON_COLOR, alphabeta_button)
        screen.blit(alphabeta_text, (alphabeta_button.x + 5, alphabeta_button.y + 10))

        pygame.draw.rect(screen, BUTTON_COLOR, new_button)
        screen.blit(new_text, (new_button.x + 33, new_button.y + 10))

        pygame.draw.rect(screen, BUTTON_COLOR, restart_button)
        screen.blit(restart_text, (restart_button.x + 20, restart_button.y + 10))

        pygame.draw.rect(screen, EXIT_BUTTON_COLOR, exit_button)
        screen.blit(exit_text, (exit_button.x + 33, exit_button.y + 10))

        # Handle button clicks
        self.handle_button_clicks(minimax_button, alphabeta_button, new_button, restart_button, exit_button)
        self.handle_ai_move()

    def handle_button_clicks(self, minimax_button, alphabeta_button, new_button, restart_button, exit_button):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if not self.game_over:
                    if minimax_button.collidepoint(pos):
                        print("Minimax button clicked")
                        self.handle_ai_move("Minimax")
                    elif alphabeta_button.collidepoint(pos):
                        print("Alpha-Beta button clicked")
                        self.handle_ai_move("AlphaBeta")
                if new_button.collidepoint(pos):
                    print("New button clicked")
                    self.reset_game()
                elif restart_button.collidepoint(pos):
                    print("Restart button clicked")
                    self.reset_game()
                elif exit_button.collidepoint(pos):
                    pygame.quit()
                    sys.exit()
    
    def handle_ai_move(self, algorithm=None):
        if algorithm is not None:
            self.ai_algorithm = algorithm

        if self.turn == 1 and not self.game_over:
            valid_moves = [col for col in range(COLS) if self.is_valid_location(col)]
            if self.ai_algorithm == "Minimax":
                col = self.minimax(4, -math.inf, math.inf, True, valid_moves)
            else:
                col = self.alphabeta(4, -math.inf, math.inf, True, valid_moves)

            if self.drop_piece(col, player=1):
                self.turn = 1  # Switch to the player's turn
                if self.check_win(1):
                    self.show_gameover(1)
                    self.game_over = True

            print(f"AI moves to column {col}")



    def reset_game(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.turn = 0
        self.game_over = False

def main():
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                col = event.pos[0] // SQUARESIZE
                row = game.get_next_open_row(col)
                if row is not None:
                    game.board[row][col] = game.turn + 1
                    game.turn ^= 1
                    if game.check_win(1):
                        game.show_gameover(1)
                        game.game_over = True
                    elif game.check_win(2):
                        game.show_gameover(2)
                        game.game_over = True
                    elif game.check_tie():
                        game.show_gameover(0)
                        game.game_over = True

        game.draw()
        pygame.display.update()

        if game.turn == 1 and not game.game_over:
            game.make_ai_move()

if __name__ == "__main__":
    main()