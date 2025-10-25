import os
import random
import pygame
from copy import deepcopy

# initializare pygame
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((400, 500))
pygame.display.set_caption("Joc 2048")
clock = pygame.time.Clock()
running = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#ecran intro
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


# culori
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


WHITE, BLACK = (255, 255, 255), (0, 0, 0)

# status joc
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

# mesaj pentru schimbare nivel
level_message_until = 0            # timestamp în ms până când se afișează mesajul
LEVEL_MESSAGE_DURATION_MS = 1500   # durată afișare mesaj în ms

# fonturi
font_small = pygame.font.SysFont(None, 18)
font_med = pygame.font.SysFont(None, 25)
font_big = pygame.font.SysFont(None, 40)
font_music = pygame.font.SysFont(None, 15)  # font special pentru muzică

#muzica de fundal
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
background_music = pygame.mixer.music.load(os.path.join(BASE_DIR, "hypnotic_jewels.ogg"))
pygame.mixer.music.set_volume(0.5)  # volum la 50%
pygame.mixer.music.play(-1)  # -1 înseamnă loop infinit
music_playing = True

def toggle_music():
    global music_playing
    if music_playing:
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()
    music_playing = not music_playing

def spawn_tile(board):
    empties = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0]
    if not empties:
        return False
    r, c = random.choice(empties)
    board[r][c] = 4 if random.random() < 0.1 else 2
    return True


def can_move(board):
    return (any(board[r][c] == 0 for r in range(GRID_SIZE) for c in range(GRID_SIZE)) or
            any(board[r][c] == board[r][c+1] for r in range(GRID_SIZE) for c in range(GRID_SIZE-1)) or
            any(board[r][c] == board[r+1][c] for c in range(GRID_SIZE) for r in range(GRID_SIZE-1)))


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
    score = moves = 0
    game_over = False
    spawn_tile(grid)
    spawn_tile(grid)


# initializare joc
restart()

def next_level():
    global grid, game_over, current_level, GRID_SIZE, level_message_until
    current_level += 1
    GRID_SIZE += 1
    new_grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            new_grid[r][c] = grid[r][c]
    grid, game_over = new_grid, False
    spawn_tile(grid)
    level_message_until = pygame.time.get_ticks() + LEVEL_MESSAGE_DURATION_MS

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
            elif event.key == pygame.K_m:
                toggle_music()
            else:
                moves_dict = {pygame.K_UP: move_up, pygame.K_DOWN: move_down, 
                             pygame.K_LEFT: move_left, pygame.K_RIGHT: move_right}
                if event.key in moves_dict:
                    new_grid, moved = moves_dict[event.key](grid)
                    if moved:
                        grid, moved_this_frame = new_grid, True
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                restart()

    if moved_this_frame:
        moves += 1
        spawn_tile(grid)
        # verificare nivel
        target = LEVEL_TARGETS.get(current_level)
        if target and any(grid[r][c] >= target for r in range(GRID_SIZE) for c in range(GRID_SIZE)):
            next_level()
    
    # verificare game over
    if not can_move(grid):
        game_over = True
        if score > high_score:
            high_score = score
    


  # fundal
    screen.fill(BACKGROUND_COLOR)
    screen.blit(background_img, (0, 0))

    # fundal tabla (folosim 360x360 ca zonă)
    board_x, board_y = 20, 120
    board_size = 360
    pygame.draw.rect(screen, WHITE, (board_x, board_y, board_size, board_size), border_radius=10)

    # calculăm dimensiunea celulelor în funcție de GRID_SIZE
    padding = 10
    total_padding = padding * (GRID_SIZE + 1)
    cell_size = max(10, (board_size - total_padding) // GRID_SIZE)

    # deseneaza patratelele
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            val = grid[r][c]
            x, y = board_x + padding + c * (cell_size + padding), board_y + padding + r * (cell_size + padding)
            tile_rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(screen, TILE_COLORS.get(val, EMPTY_COLOR), tile_rect, border_radius=5)
            if val:
                font_size = max(12, int(cell_size * 0.6) - (len(str(val)) - 1) * 4)
                surf = pygame.font.SysFont(None, font_size, bold=True).render(str(val), True, WHITE)
                screen.blit(surf, surf.get_rect(center=tile_rect.center))

    # UI text
    texts = [
        (f'High Score: {high_score}', (20, 10)),
        (f'Level: {current_level}', (20, 80)),
        (f'Move: {moves}', (300, 40)),
        (f'Score: {score}', (300, 80)),
        (f'Music: {"ON" if music_playing else "OFF"} (M)', (300, 10))
    ]
    for text, pos in texts:
        font = font_music if 'Music' in text else font_med
        screen.blit(font.render(text, True, WHITE), pos)

    # overlays
    if pygame.time.get_ticks() < level_message_until:
        overlay = pygame.Surface((360, 80), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        msg = font_big.render(f'Level {current_level}', True, WHITE)
        screen.blit(overlay, (20, 140))
        screen.blit(msg, (20 + (360 - msg.get_width()) // 2, 140 + (80 - msg.get_height()) // 2))
    if game_over:
        overlay = pygame.Surface((360, 360), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        screen.blit(overlay, (20, 120))
        for text, y in [('Game Over!', 230), ('Press R to Restart', 280)]:
            font = font_big if 'Game' in text else font_med
            surf = font.render(text, True, BLACK)
            screen.blit(surf, (200 - surf.get_width()//2, y))

    # update display
    pygame.display.flip()
    clock.tick(60)  # FPS

pygame.quit()