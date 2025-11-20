# joc_2048.py
# Versiune corectată: bara de volum apare doar în ecranul MENU,
# butonul Difficulty este în MENU și funcțional (poți schimba dificultatea și reveni la meniu).
# Spawn logic: Easy / Medium / Hard (hard = mai agresiv + obstacole ocazionale).

import os
import random
import pygame
import math

# -------------------- Init --------------------
pygame.init()
pygame.font.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Fereastra
WIDTH, HEIGHT = 400, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Joc 2048")
clock = pygame.time.Clock()
FPS = 60

# volum master
volum = 0.5

# fonturi
intro_font = pygame.font.SysFont(None, 40, bold=True)
font_small = pygame.font.SysFont(None, 18)
font_med = pygame.font.SysFont(None, 25)
font_big = pygame.font.SysFont(None, 40)
font_music = pygame.font.SysFont(None, 15)

# imagini
intro_image = pygame.image.load(os.path.join(BASE_DIR, "intro_bck.png"))
intro_image = pygame.transform.scale(intro_image, (WIDTH, HEIGHT))
background_img = pygame.image.load(os.path.join(BASE_DIR, "fundal_joc.png"))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# culori / tile colors
BACKGROUND_COLOR = (187, 173, 160)
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
EMPTY_COLOR = (205, 193, 180)
OBSTACLE_COLOR = (50, 36, 36)
TILE_COLORS = {
    2: (255, 95, 109),
    4: (255, 146, 76),
    8: (255, 204, 102),
    16: (120, 220, 130),
    32: (72, 202, 228),
    64: (96, 110, 255),
    128: (159, 94, 255),
    256: (255, 94, 247),
    512: (255, 64, 129),
    1024: (255, 51, 102),
    2048: (255, 255, 255),
    4096: (255, 255, 160),
    8192: (255, 255, 210)
}

# -------------------- Sunet --------------------
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pop_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "pop_block_fx.wav"))
lvl_up_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "level_up_fx.wav"))
game_over_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "game_over_fx.wav"))
pop_base = 0.6
lvl_up_base = 0.6
game_over_base = 0.8

pygame.mixer.music.load(os.path.join(BASE_DIR, "hypnotic_jewels.ogg"))
pygame.mixer.music.play(-1)

def set_master_volume(v):
    global volum
    volum = max(0.0, min(1.0, v))
    pygame.mixer.music.set_volume(volum)
    pop_sound.set_volume(volum * pop_base)
    lvl_up_sound.set_volume(volum * lvl_up_base)
    game_over_sound.set_volume(volum * game_over_base)

set_master_volume(volum)

# -------------------- UI / Menu --------------------
btn_w, btn_h = 200, 40
btn_x = (WIDTH - btn_w) // 2
btn_start_y = 200
btn_gap = 20
btn_play = pygame.Rect(btn_x, btn_start_y, btn_w, btn_h)
btn_menu = pygame.Rect(btn_x, btn_start_y + (btn_h + btn_gap), btn_w, btn_h)
btn_credits = pygame.Rect(btn_x, btn_start_y + 2*(btn_h + btn_gap), btn_w, btn_h)
# Difficulty button should be visible in MENU (not in main)
btn_difficulty = pygame.Rect(btn_x, btn_start_y + 2.5*(btn_h + btn_gap), btn_w, btn_h)
back_btn = pygame.Rect(20, 440, 80, 30)

# slider variables used only in MENU
buton_activ = False
menu_slider_x, menu_slider_y = 100, 300
menu_slider_len = 200
buton_radius = 10

def draw_button(surf, rect, text, font, bg=(50,50,50), fg=(0,0,0)):
    pygame.draw.rect(surf, bg, rect, border_radius=8)
    txt = font.render(text, True, fg)
    surf.blit(txt, txt.get_rect(center=rect.center))

# -------------------- Game state --------------------
GRID_SIZE = 4
grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
score = 0
moves = 0
high_score = 0
game_over = False

current_level = 1
LEVEL_TARGETS = {1:128, 2:1024, 3:2048, 4:4096, 5:8192}

LEVEL_MESSAGE_DURATION_MS = 3000
level_message_until = 0

music_playing = True

# difficulty
selected_difficulty = "easy"  # default: easy / medium / hard

# -------------------- Spawn logic per difficulty --------------------
def spawn_tile(board, prefer_four=False):
    empties = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0]
    if not empties:
        return None
    r, c = random.choice(empties)
    # prefer_four: higher chance to be 4
    if prefer_four:
        val = 4 if random.random() < 0.9 else 2
    else:
        val = 4 if random.random() < 0.1 else 2
    board[r][c] = val
    return (r, c, val)

def spawn_tiles_for_level(board, level, count=None, force_four=False):
    if count is None:
        count = max(1, level)
    spawned = []
    if force_four:
        empties = [(r,c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0]
        if empties:
            r,c = random.choice(empties)
            board[r][c] = 4
            spawned.append((r,c,4))
    for _ in range(count - len(spawned)):
        s = spawn_tile(board, prefer_four=False)
        if s:
            spawned.append(s)
        else:
            break
    return spawned

def place_obstacle(board):
    empties = [(r,c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0]
    if not empties:
        return None
    r,c = random.choice(empties)
    board[r][c] = -1
    return (r,c)

# -------------------- Movement & merge --------------------
def can_move(board):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            val = board[r][c]
            if val == 0:
                return True
            if val == -1:
                continue
            if c + 1 < GRID_SIZE:
                v2 = board[r][c+1]
                if v2 != -1 and val == v2:
                    return True
            if r + 1 < GRID_SIZE:
                v2 = board[r+1][c]
                if v2 != -1 and val == v2:
                    return True
    return False

def compress_row_left(row):
    new = [v for v in row if v != 0 and v != -1]
    obstacle_indices = [i for i, val in enumerate(row) if val == -1]
    base = [0] * len(row)
    cur = 0
    for v in new:
        base[cur] = v
        cur += 1
    result = []
    iter_vals = [v for v in base if v != 0]
    idx_iter = 0
    for i in range(len(row)):
        if i in obstacle_indices:
            result.append(-1)
        else:
            if idx_iter < len(iter_vals):
                result.append(iter_vals[idx_iter])
                idx_iter += 1
            else:
                result.append(0)
    return result

def merge_row_left(row):
    gained = 0
    # split into segments separated by obstacles
    segments = []
    seg_indices = []
    start = 0
    for i, val in enumerate(row):
        if val == -1:
            segments.append(row[start:i])
            seg_indices.append((start, i-1))
            start = i+1
    segments.append(row[start:len(row)])
    seg_indices.append((start, len(row)-1))
    new_row = [None] * len(row)
    for i, v in enumerate(row):
        if v == -1:
            new_row[i] = -1
    for seg_idx, seg in zip(seg_indices, segments):
        compact = [v for v in seg if v != 0]
        merged_seg = []
        j = 0
        while j < len(compact):
            if j + 1 < len(compact) and compact[j] == compact[j+1]:
                merged_val = compact[j] * 2
                merged_seg.append(merged_val)
                gained += merged_val
                pop_sound.play()
                j += 2
            else:
                merged_seg.append(compact[j])
                j += 1
        seg_len = len(seg)
        merged_seg += [0] * (seg_len - len(merged_seg))
        start_idx = seg_idx[0]
        for k in range(seg_len):
            if new_row[start_idx + k] is None:
                new_row[start_idx + k] = merged_seg[k]
    for i in range(len(new_row)):
        if new_row[i] is None:
            new_row[i] = 0
    return new_row, gained

def move_left(board):
    moved = False
    new_board = []
    total_gained = 0
    for r in range(GRID_SIZE):
        row = board[r]
        compressed = compress_row_left(row)
        merged, gained = merge_row_left(compressed)
        if merged != row:
            moved = True
        new_board.append(merged)
        total_gained += gained
    return new_board, moved, total_gained

def transpose(board):
    return [list(row) for row in zip(*board)]

def move_right(board):
    rev = [list(reversed(row)) for row in board]
    moved_board, moved, gained = move_left(rev)
    result = [list(reversed(row)) for row in moved_board]
    return result, moved, gained

def move_up(board):
    t = transpose(board)
    moved_board, moved, gained = move_left(t)
    return transpose(moved_board), moved, gained

def move_down(board):
    t = transpose(board)
    moved_board, moved, gained = move_right(t)
    return transpose(moved_board), moved, gained

# -------------------- Restart / level --------------------
def restart():
    global grid, score, moves, game_over, current_level, GRID_SIZE
    GRID_SIZE = 4
    current_level = 1
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    score = 0
    moves = 0
    game_over = False
    spawn_tile(grid)
    spawn_tile(grid)

def next_level():
    global grid, game_over, current_level, GRID_SIZE, level_message_until
    current_level += 1
    new_size = GRID_SIZE + 1
    old = grid
    GRID_SIZE = new_size
    new_grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
    for r in range(len(old)):
        for c in range(len(old[r])):
            new_grid[r][c] = old[r][c]
    grid[:] = new_grid
    game_over = False
    spawn_tile(grid)
    lvl_up_sound.play()
    level_message_until = pygame.time.get_ticks() + LEVEL_MESSAGE_DURATION_MS

# -------------------- Drawing --------------------
def draw_board(board):
    board_x, board_y = 20, 120
    board_size = 360
    padding = 10
    total_padding = padding * (GRID_SIZE + 1)
    cell_size = max(10, (board_size - total_padding) // GRID_SIZE)

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            val = board[r][c]
            x = board_x + padding + c * (cell_size + padding)
            y = board_y + padding + r * (cell_size + padding)
            tile_rect = pygame.Rect(x, y, cell_size, cell_size)
            if val == -1:
                pygame.draw.rect(screen, OBSTACLE_COLOR, tile_rect, border_radius=5)
                surf = font_small.render("nigga", True, WHITE)
                screen.blit(surf, surf.get_rect(center=tile_rect.center))
                continue
            color = TILE_COLORS.get(val, EMPTY_COLOR)
            pygame.draw.rect(screen, color, tile_rect, border_radius=5)
            if val and val != -1:
                font_size = max(12, int(cell_size * 0.6) - (len(str(val)) - 1) * 4)
                surf = pygame.font.SysFont(None, font_size, bold=True).render(str(val), True, WHITE)
                screen.blit(surf, surf.get_rect(center=tile_rect.center))
    return (board_x, board_y, cell_size, padding)

# -------------------- Intro/Menu flow --------------------
intro_state = 'main'   # 'main', 'menu', 'credits', 'difficulty'
show_intro = True

restart()
pygame.mixer.music.set_volume(volum)

# -------------------- Main loop --------------------
running = True
while running:
    # Intro loop
    while show_intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if intro_state == 'main':
                    show_intro = False
                else:
                    intro_state = 'main'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if intro_state == 'main':
                    if btn_play.collidepoint((mx,my)):
                        show_intro = False
                    elif btn_menu.collidepoint((mx,my)):
                        intro_state = 'menu'
                    elif btn_credits.collidepoint((mx,my)):
                        intro_state = 'credits'
                elif intro_state == 'menu':
                    if btn_difficulty.collidepoint((mx,my)):
                        intro_state = 'difficulty'
                elif intro_state == 'difficulty':
                    # clicks in difficulty screen are handled below with rect checks
                    pass
                else:
                    if back_btn.collidepoint((mx,my)):
                        intro_state = 'main'

            # slider in menu (mouse down handled above; here we only track mouse motion)
            if intro_state == 'menu':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx,my = event.pos
                    if menu_slider_x <= mx <= menu_slider_x + menu_slider_len and abs(my - menu_slider_y) < 20:
                        buton_activ = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    buton_activ = False
                elif event.type == pygame.MOUSEMOTION and buton_activ:
                    mx,my = event.pos
                    v = max(0.0, min(1.0, (mx - menu_slider_x) / menu_slider_len))
                    set_master_volume(v)

        # draw intro/menu screens
        screen.fill((0,0,0))
        screen.blit(intro_image, (0,0))

        if intro_state == 'main':
            draw_button(screen, btn_play, "Play", intro_font, bg=(130,255,100))
            draw_button(screen, btn_menu, "Menu", intro_font, bg=(255,100,100))
            draw_button(screen, btn_credits, "Credits", intro_font, bg=(130,30,90))
            hint = font_small.render('Press any key to start or click Play', True, (255,255,255))
            screen.blit(hint, (20,460))

        elif intro_state == 'menu':
            overlay = pygame.Surface((360,300), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (20,100))
            hdr = font_big.render('Menu', True, (255,255,255))
            screen.blit(hdr, (200 - hdr.get_width()//2, 160))
            info = font_med.render('Setări', True, (200,200,200))
            screen.blit(info, (200 - info.get_width()//2, 210))
            draw_button(screen, back_btn, "Back", font_small, bg=(70,70,70))

            # difficulty button inside MENU (user asked specifically)
            draw_button(screen, btn_difficulty, "Difficulty", font_med, bg=(90,150,255))

            # volume slider shown only in MENU
            pygame.draw.line(screen, (180,180,180), (menu_slider_x, menu_slider_y), (menu_slider_x + menu_slider_len, menu_slider_y), 4)
            pos = menu_slider_x + int(volum * menu_slider_len)
            pygame.draw.circle(screen, (255,100,100), (pos, menu_slider_y), buton_radius)
            label = font_small.render(f"Volum: {int(volum*100)}%", True, (255,255,255))
            screen.blit(label, (200 - label.get_width()//2, menu_slider_y + 20))

            # show current difficulty
            diff_label = font_med.render(f'Difficulty: {selected_difficulty.upper()}', True, (255,255,255))
            screen.blit(diff_label, (200 - diff_label.get_width()//2, 250 - 60))

        elif intro_state == 'difficulty':
            overlay = pygame.Surface((360,300), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (20,100))
            hdr = font_big.render('Alege dificultatea', True, (255,255,255))
            screen.blit(hdr, (200 - hdr.get_width()//2, 130))

            btn_easy = pygame.Rect(100, 180, 200, 40)
            btn_medium = pygame.Rect(100, 230, 200, 40)
            btn_hard = pygame.Rect(100, 280, 200, 40)
            draw_button(screen, btn_easy, "Easy", font_med, bg=(80,200,80))
            draw_button(screen, btn_medium, "Medium", font_med, bg=(200,200,80))
            draw_button(screen, btn_hard, "Hard", font_med, bg=(200,80,80))
            draw_button(screen, back_btn, "Back", font_small, bg=(70,70,70))

            # handle clicks by polling mouse state on press
            # but better to check MOUSEBUTTONDOWN events; check current mouse state only if clicked
            if pygame.mouse.get_pressed()[0]:
                mx,my = pygame.mouse.get_pos()
                # small debounce: require cursor to be within button area for selection
                if btn_easy.collidepoint((mx,my)):
                    selected_difficulty = "easy"
                    intro_state = 'menu'   # go back to menu after selection
                elif btn_medium.collidepoint((mx,my)):
                    selected_difficulty = "medium"
                    intro_state = 'menu'
                elif btn_hard.collidepoint((mx,my)):
                    selected_difficulty = "hard"
                    intro_state = 'menu'
                elif back_btn.collidepoint((mx,my)):
                    intro_state = 'menu'

        else:  # credits
            overlay = pygame.Surface((360,300), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (20,100))
            hdr = font_big.render('Credits', True, (255,255,255))
            screen.blit(hdr, (200 - hdr.get_width()//2, 140))
            lines = [
                "Creatori:",
                "Cănuță Andrei, Ciufu Andrei Laurențiu",
                "Muzică: 'Hypnotic Jewels'",
                "by Eric Matyas soundimage.org"
            ]
            for i, ln in enumerate(lines):
                surf = font_med.render(ln, True, (220,220,220))
                screen.blit(surf, (200 - surf.get_width()//2, 190 + i*30))
            draw_button(screen, back_btn, "Back", font_small, bg=(70,70,70))

        pygame.display.update()
        clock.tick(30)

    # Gameplay events
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
                if music_playing:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
                music_playing = not music_playing
            else:
                moves_dict = {
                    pygame.K_UP: move_up,
                    pygame.K_DOWN: move_down,
                    pygame.K_LEFT: move_left,
                    pygame.K_RIGHT: move_right
                }
                if event.key in moves_dict:
                    new_grid, moved, gained = moves_dict[event.key](grid)
                    if moved:
                        grid[:] = new_grid
                        score += gained
                        moves += 1
                        moved_this_frame = True
                        # spawning logic per difficulty (aplicată imediat după mutare)
                        if selected_difficulty == "easy":
                            spawn_tiles_for_level(grid, 1, count=1)
                        elif selected_difficulty == "medium":
                            spawn_tiles_for_level(grid, current_level, count=max(1, current_level))
                        elif selected_difficulty == "hard":
                            spawn_tiles_for_level(grid, current_level, count=max(1, current_level+1), force_four=True)
                            if moves % 5 == 0:
                                place_obstacle(grid)
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                restart()

        # MENU slider events are handled in intro loop; no in-game slider events here

    # level check
    target = LEVEL_TARGETS.get(current_level)
    if target and any(grid[r][c] >= target for r in range(GRID_SIZE) for c in range(GRID_SIZE)):
        next_level()

    # game over check
    if not can_move(grid) and not game_over:
        game_over = True
        game_over_sound.play()
        if music_playing:
            pygame.mixer.music.pause()
            music_playing = False
        if score > high_score:
            high_score = score

    # Draw frame
    screen.fill(BACKGROUND_COLOR)
    screen.blit(background_img, (0, 0))

    # board background
    board_x, board_y = 20, 120
    board_size = 360
    pygame.draw.rect(screen, WHITE, (board_x, board_y, board_size, board_size), border_radius=10)

    # draw tiles
    draw_board(grid)

    # UI text
    texts = [
        (f'High Score: {high_score}', (20, 10)),
        (f'Level: {current_level}', (20, 80)),
        (f'Move: {moves}', (300, 40)),
        (f'Score: {score}', (300, 80)),
        (f'Difficulty: {selected_difficulty.upper()}', (20, 40)),
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

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
