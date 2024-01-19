import numpy as np
import random
import pygame
import sys
import math
import time
import pygame_gui


# Log window dimensions
LOG_WIDTH = 100
LOG_HEIGHT = 100

# Scroll bar width
BAR_WIDTH = 20
color1=(0,0,0)
# Log window
log_surface = pygame.Surface((LOG_WIDTH, LOG_HEIGHT))
log_surface.fill(color1)
color2=(0,255,0)
log_text=[]
class Scrollbar:
   def __init__(self, x, y, height):
      self.x = x
      self.y = y
      self.height = height
      self.surface = pygame.Surface((BAR_WIDTH, self.height))
      self.surface.fill(BLACK)
      self.rect = self.surface.get_rect(topleft=(x, y))
      self.thumb_height = 100
      self.thumb = pygame.Rect(0, 0, BAR_WIDTH, self.thumb_height)

   def draw(self, win):
       win.blit(self.surface, self.rect)
       pygame.draw.rect(win, color2, self.thumb)

   def update(self, win, log):
       total_height = len(log) * 20
       self.thumb_height = int(self.height / total_height * self.height)
       self.thumb.height = self.thumb_height

       win.blit(self.surface, self.rect)
       pygame.draw.rect(win, color2, self.thumb)

def draw_log(log_text):
    # Draw lines onto log surface
    log_surface.fill(color1)
    for i, text in enumerate(log_text):
        img = font.render(text, True, BLACK)
        log_surface.blit(img, (10, i * 20))
    pygame.display.update()

pygame.init()
# Font for drawing text
font = pygame.font.Font(None, 30)
nodes=0
def draw_text(text, font, color, x, y):
  img = font.render(text, True, color)
  screen.blit(img, (x, y))
# Create log surface
log_surface = pygame.Surface((400, 500))

log_surface.fill(color1)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                c + 3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                c] == piece:
                return True

    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][
                c + 3] == piece:
                return True

    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][
                c + 3] == piece:
                return True

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def score_position(board, piece):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score posiive sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board, depth, alpha, beta, maximizingPlayer):
    global nodes
    nodes+=1
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col


def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (
            int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (
                int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (
                int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()



board = create_board()
print_board(board)
game_over = False

pygame.init()

SQUARESIZE = 50

width = 800#(COLUMN_COUNT * SQUARESIZE)* SQUARESIZE/50
height = (ROW_COUNT + 1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode(size)

# Draw board at same position
for c in range(COLUMN_COUNT):
    for r in range(ROW_COUNT):
        pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER, AI)

draw_text("mini_max", font, BLUE, 350, 150)


new_game_btn = pygame.Surface((135, 40))
restart_btn = pygame.Surface((100, 40))
exit_btn = pygame.Surface((100, 40))

new_game_btn.fill(BLUE)
restart_btn.fill(BLUE)
exit_btn.fill(BLUE)

new_game_text = font.render("New Game", True, RED)
restart_text = font.render("Restart", True, RED)
exit_text = font.render("Exit", True, RED)

new_game_btn.blit(new_game_text, (20, 10))
restart_btn.blit(restart_text, (10, 10))
exit_btn.blit(exit_text, (10, 10))

new_game_rect = new_game_btn.get_rect(topleft=(360, 300))
restart_rect = restart_btn.get_rect(topleft=(550, 300))
exit_rect = exit_btn.get_rect(topleft=(700, 300))

screen.blit(new_game_btn, new_game_rect)
screen.blit(restart_btn, restart_rect)
screen.blit(exit_btn, exit_rect)

def create_board():
  board = np.zeros((6, 7))
  return board

while not game_over:
    if turn == PLAYER:
        draw_text("Player's Turn", font, RED, 350, 100)
        #pygame.draw.rect(screen, BLACK, (350, 100, 150, 20))
    else:
        draw_text("AI's Turn", font, YELLOW, 350, 100)
        pygame.draw.rect(screen, BLACK, (350, 100, 150, 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        dot_drawn = False
        if event.type == pygame.MOUSEMOTION:
            if dot_drawn:
                pygame.draw.rect(screen, BLACK, (0, 0, 400, SQUARESIZE))
                dot_drawn = False

            posx = event.pos[0]
            if posx < 400:
                if turn == PLAYER:
                    dot_drawn = True
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)

                # Redraw background rect
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            """
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
            """

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            #pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            # print(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN:

                if new_game_rect.collidepoint(event.pos):
                    board = create_board()  # Create new board
                    game_over = False  # Reset game over
                    turn = random.randint(PLAYER, AI)

                if restart_rect.collidepoint(event.pos):
                    board = create_board()  # New board
                    game_over = False  # Reset flag
                    turn = 0  # Player starts

                if exit_rect.collidepoint(event.pos):
                    sys.exit()
                # Ask for Player 1 Input
                if turn == PLAYER:
                    posx = event.pos[0]
                    if posx < 400:
                        col = int(math.floor(posx / SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)

                        if winning_move(board, PLAYER_PIECE):
                            label = myfont.render("Player 1 wins!!", 1, RED)
                            screen.blit(label, (40, 10))
                            game_over = True

                        turn += 1
                        turn = turn % 2

                        print_board(board)
                        draw_board(board)
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
    # # Ask for Player 2 Input
    if turn == AI and not game_over:

        # col = random.randint(0, COLUMN_COUNT-1)
        # col = pick_best_move(board, AI_PIECE)
        pygame.draw.rect(screen, BLACK, (450,200,300,100))
        start = time.time()
        #nodes=0
        col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
        #minimax function call
        end = time.time()
        duration = end - start
        draw_text("Thinking time: " + str(duration), font, RED, 350, 200)
        draw_text("Nodes explored: " + str(nodes), font, RED, 350, 250)
        #scrollbar = Scrollbar(500, 250, LOG_HEIGHT)
        #log_text.append("Nodes explored: " + str(nodes))
        #draw_log(log_text)
        if is_valid_location(board, col):
            # pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = myfont.render("Player 2 wins!!", 1, YELLOW)
                screen.blit(label, (40, 10))
                game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)