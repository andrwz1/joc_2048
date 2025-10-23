import os
import random
import pygame
from copy import deepcopy

# game setup
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((400, 500))
pygame.display.set_caption("Joc 2048")
clock = pygame.time.Clock()
running = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#intro screen
intro_font = pygame.font.SysFont(None, 30, bold=True)
intro_text = intro_font.render('Press any key to start', True, (255, 255, 255))
intro_image = pygame.image.load(os.path.join(BASE_DIR, "intro_bck.png"))
intro_image = pygame.transform.scale(intro_image, (400, 500))
show_intro = True
while show_intro:
    screen.fill((255, 255, 255))
    screen.blit(intro_image, (0, 0))
    screen.blit(intro_text, (100, 450))
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            show_intro = False


# colors
BACKGROUND_COLOR = (187, 173, 160)
background_img = pygame.image.load(os.path.join(BASE_DIR, "fundal_joc.png"))
background_img = pygame.transform.scale(background_img, (400, 500))


EMPTY_COLOR = (205, 193, 180)
TILE_COLORS = {
    2: (255, 95, 109),      # coral cald
    4: (255, 146, 76),      # portocaliu bogat
    8: (255, 204, 102),     # galben luminos
    16: (120, 220, 130),    # verde smarald curat
    32: (72, 202, 228),     # cyan saturat
    64: (96, 110, 255),     # albastru indigo
    128: (159, 94, 255),    # mov intens
    256: (255, 94, 247),    # roz neon
    512: (255, 64, 129),    # fucsia adânc
    1024: (255, 51, 102),   # roșu saturat
    2048: (255, 255, 255),  # alb luminos
    4096: (255, 255, 160),  # galben-alb pal, efect “glow”
    8192: (255, 255, 210)   # alb cald, highlight final
}


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# game state
GRID_SIZE = 4
grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
score = 0
moves = 0
high_score = 0
game_over = False

# tinte pentru urmatorul nivel
current_level = 1
LEVEL_TARGETS = {
    1: 128,
    2: 1024,
    3: 2048,
    4: 4096,
    5: 8192
}

# fonts
font_small = pygame.font.SysFont(None, 18)
font_med = pygame.font.SysFont(None, 25)
font_big = pygame.font.SysFont(None, 40)


def spawn_tile(board):
    empties = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0]
    if not empties:
        return False
    r, c = random.choice(empties)
    board[r][c] = 4 if random.random() < 0.1 else 2
    return True


def can_move(board):
    # if any empty exist -> can move
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board[r][c] == 0:
                return True
    # check merges horizontally and vertically
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 1):
            if board[r][c] == board[r][c + 1]:
                return True
    for c in range(GRID_SIZE):
        for r in range(GRID_SIZE - 1):
            if board[r][c] == board[r + 1][c]:
                return True
    return False


def compress_row_left(row):
    # remove zeros, keep order
    new = [v for v in row if v != 0]
    new += [0] * (len(row) - len(new))
    return new


def merge_row_left(row):
    global score
    row = compress_row_left(row)
    merged = [False] * len(row)
    for i in range(len(row) - 1):
        if row[i] != 0 and row[i] == row[i + 1] and not merged[i] and not merged[i + 1]:
            row[i] *= 2
            row[i + 1] = 0
            merged[i] = True
            score += 1
    return compress_row_left(row)


def move_left(board):
    moved = False
    new_board = []
    for r in range(GRID_SIZE):
        new_row = merge_row_left(board[r])
        if new_row != board[r]:
            moved = True
        new_board.append(new_row)
    return new_board, moved


def move_right(board):
    # reverse each row, move left, reverse back
    rev = [list(reversed(row)) for row in board]
    moved_board, moved = move_left(rev)
    return [list(reversed(row)) for row in moved_board], moved


def transpose(board):
    return [list(row) for row in zip(*board)]


def move_up(board):
    t = transpose(board)
    moved_board, moved = move_left(t)
    return transpose(moved_board), moved


def move_down(board):
    t = transpose(board)
    moved_board, moved = move_right(t)
    return transpose(moved_board), moved


def restart():
    global grid, score, moves, game_over
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    score = 0
    moves = 0
    game_over = False
    spawn_tile(grid)
    spawn_tile(grid)


def new_level():
    global grid, score, moves, game_over
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    score = 0
    moves = 0
    game_over = False
    spawn_tile(grid)
    spawn_tile(grid)


# initialize
restart()
if high_score < score:
    high_score = score

def next_level():
    global grid, score, moves, game_over, current_level
    # avansăm nivelul
    current_level += 1
    # resetăm tabla pentru nivelul următor (configurabil dacă doriți păstrarea scorului)
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    score = 0
    moves = 0
    game_over = False
    # spawn două piese de start
    spawn_tile(grid)
    spawn_tile(grid)

# main loop
while running:
    moved_this_frame = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_r:
                restart()
            elif event.key == pygame.K_UP:
                new_grid, moved = move_up(grid)
                if moved:
                    grid = new_grid
                    moved_this_frame = True
            elif event.key == pygame.K_DOWN:
                new_grid, moved = move_down(grid)
                if moved:
                    grid = new_grid
                    moved_this_frame = True
            elif event.key == pygame.K_LEFT:
                new_grid, moved = move_left(grid)
                if moved:
                    grid = new_grid
                    moved_this_frame = True
            elif event.key == pygame.K_RIGHT:
                new_grid, moved = move_right(grid)
                if moved:
                    grid = new_grid
                    moved_this_frame = True
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                restart()

    if moved_this_frame:
        moves += 1
        spawn_tile(grid)

 # verificare nivel: dacă există un tile >= țintă pentru nivelul curent, trecem la nivelul următor
        target = LEVEL_TARGETS.get(current_level)
        if target is not None:
            found = False
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if grid[r][c] >= target:
                        found = True
                        break
                if found:
                    break
            if found:
                next_level()
                # după next_level am resetat tabla și mutările; sar peste verificarea can_move în acest cadru
        
        if not can_move(grid):
            game_over = True
            if score > high_score:
                high_score = score
    


    # draw background
    screen.fill(BACKGROUND_COLOR)
    screen.blit(background_img, (0, 0))

    # board background
    pygame.draw.rect(screen, WHITE, (20, 120, 360, 360), border_radius=10)

    # draw grid tiles
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            val = grid[r][c]
            x = 30 + c * 90
            y = 130 + r * 90
            tile_rect = pygame.Rect(x, y, 80, 80)
            color = TILE_COLORS.get(val, EMPTY_COLOR) if val != 0 else EMPTY_COLOR
            pygame.draw.rect(screen, color, tile_rect, border_radius=5)
            if val != 0:
                # choose text color depending on tile
                txt_color = WHITE
                # pick font size based on number width
                txt = str(val)
                # center text
                font_size = 36 if val < 100 else (28 if val < 1000 else 22)
                font_tile = pygame.font.SysFont(None, font_size, bold=True)
                surf = font_tile.render(txt, True, txt_color)
                rect = surf.get_rect(center=tile_rect.center)
                screen.blit(surf, rect)



    # move, score, level, high score
    move_surface = font_med.render(f'Move: {moves}', True, WHITE)
    screen.blit(move_surface, (300, 40))

    score_surface = font_med.render(f'Score: {score}', True, WHITE)
    screen.blit(score_surface, (300, 80))

    level_surface = font_med.render('Level: 1', True, WHITE)
    screen.blit(level_surface, (20, 80))

    high_score_surface = font_med.render(f'High Score: {high_score}', True, WHITE)
    screen.blit(high_score_surface, (20, 40))

    level_surface = font_med.render(f'Level: {current_level}', True, WHITE)
    screen.blit(level_surface, (20, 80))

    # game over overlay
    if game_over:
        overlay = pygame.Surface((360, 360), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        screen.blit(overlay, (20, 120))
        go_surf = font_big.render('Game Over!', True, BLACK)
        screen.blit(go_surf, (400//2 - go_surf.get_width()//2, 230))
        sub_surf = font_med.render('Press R to Restart', True, BLACK)
        screen.blit(sub_surf, (400//2 - sub_surf.get_width()//2, 280))

    # update display
    pygame.display.flip()
    clock.tick(60)  # FPS

pygame.quit()