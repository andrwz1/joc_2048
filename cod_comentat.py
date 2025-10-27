"""
Joc 2048 - Implementare în Python cu Pygame

Acest joc este o versiune îmbunătățită a jocului clasic 2048 cu următoarele caracteristici:
- Interfață grafică cu pygame
- Sistem de nivele progresive (grid-ul crește de la 4x4 la 8x8)
- Muzică de fundal
- Meniu introductiv cu opțiuni
- Sistem de scor și high score
- Culori vibrante pentru fiecare valoare de tile

Controale:
- Săgeți: Mută tiles-urile
- R: Restart joc
- M: Toggle muzică
- Q: Ieșire din joc

Creatori: Cănuță Andrei, Ciufu Andrei Laurențiu
"""

import os
import random
import pygame
from copy import deepcopy

# =============================================================================
# CONSTANTE ȘI CONFIGURAȚII GLOBALE
# =============================================================================

# Configurații ecran și joc
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 500
FPS = 60
INTRO_FPS = 30

# Configurații pentru meniul introductiv
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 40
BUTTON_START_Y = 200
BUTTON_GAP = 20

# Configurații pentru tabla de joc
BOARD_X = 20
BOARD_Y = 120
BOARD_SIZE = 360
CELL_PADDING = 10

# Configurații pentru fonturi
INTRO_FONT_SIZE = 40
SMALL_FONT_SIZE = 18
MEDIUM_FONT_SIZE = 25
BIG_FONT_SIZE = 40
MUSIC_FONT_SIZE = 15

# Configurații pentru muzică
MUSIC_VOLUME = 0.5
MUSIC_FREQUENCY = 44100
MUSIC_CHANNELS = 2
MUSIC_BUFFER = 512

# Configurații pentru nivele
LEVEL_MESSAGE_DURATION_MS = 2000
DEFAULT_GRID_SIZE = 4

# Configurații pentru tiles
TILE_SPAWN_PROBABILITY_4 = 0.1  # 10% șanse pentru tile-ul 4

# Directorul curent pentru încărcarea resurselor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# INIȚIALIZARE PYGAME
# =============================================================================

# Inițializare pygame și configurare ecran
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Joc 2048")
clock = pygame.time.Clock()
running = True

# =============================================================================
# FUNCȚII PENTRU GESTIONAREA ERORILOR
# =============================================================================

def load_image_safe(path, scale_to=None):
    """
    Încarcă o imagine cu gestionarea erorilor.
    
    Args:
        path: Calea către fișierul imagine
        scale_to: Tuple (width, height) pentru scalare, opțional
        
    Returns:
        pygame.Surface sau None dacă încărcarea a eșuat
    """
    try:
        image = pygame.image.load(path)
        if scale_to:
            image = pygame.transform.scale(image, scale_to)
        return image
    except pygame.error as e:
        print(f"Eroare la încărcarea imaginii {path}: {e}")
        return None

def load_music_safe(path):
    """
    Încarcă muzica cu gestionarea erorilor.
    
    Args:
        path: Calea către fișierul muzică
        
    Returns:
        bool: True dacă încărcarea a reușit, False altfel
    """
    try:
        pygame.mixer.music.load(path)
        return True
    except pygame.error as e:
        print(f"Eroare la încărcarea muzicii {path}: {e}")
        return False

# =============================================================================
# CONFIGURAȚII FONTURI ȘI RESURSE GRAFICE
# =============================================================================

# Definirea fonturilor pentru diferite elemente UI
intro_font = pygame.font.SysFont(None, INTRO_FONT_SIZE, bold=True)  # Font pentru butoanele principale
font_small = pygame.font.SysFont(None, SMALL_FONT_SIZE)             # Font pentru text mic
font_med = pygame.font.SysFont(None, MEDIUM_FONT_SIZE)               # Font pentru text mediu
font_big = pygame.font.SysFont(None, BIG_FONT_SIZE)                 # Font pentru text mare
font_music = pygame.font.SysFont(None, MUSIC_FONT_SIZE)             # Font special pentru muzică

# Încărcarea și scalarea imaginii de fundal pentru meniul introductiv
intro_image = load_image_safe(os.path.join(BASE_DIR, "intro_bck.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
if intro_image is None:
    # Creează o imagine de fundal simplă dacă încărcarea eșuează
    intro_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    intro_image.fill((50, 50, 50))  # Fundal gri închis

# =============================================================================
# FUNCȚII UTILITARE PENTRU INTERFAȚA GRAFICĂ
# =============================================================================

def draw_button(surf, rect, text, font, bg=(50,50,50), fg=(0,0,0)):
    """
    Desenează un buton cu text pe suprafața specificată.
    
    Args:
        surf: Suprafața pygame pe care se desenează
        rect: Rectangle-ul pygame care definește poziția și dimensiunea butonului
        text: Textul care se afișează pe buton
        font: Fontul pygame pentru text
        bg: Culoarea de fundal a butonului (RGB tuple)
        fg: Culoarea textului (RGB tuple)
    """
    pygame.draw.rect(surf, bg, rect, border_radius=8)
    txt = font.render(text, True, fg)
    surf.blit(txt, txt.get_rect(center=rect.center))

# =============================================================================
# CONFIGURAȚII MENIU INTRODUCTIV
# =============================================================================

# Starea curentă a meniului introductiv
intro_state = 'main'   # 'main', 'menu', 'credits'
show_intro = True

# Configurații pentru layout-ul butoanelor
btn_x = (SCREEN_WIDTH - BUTTON_WIDTH) // 2  # Poziția X centrată

# Definirea rectangle-urilor pentru butoane
btn_play = pygame.Rect(btn_x, BUTTON_START_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
btn_menu = pygame.Rect(btn_x, BUTTON_START_Y + (BUTTON_HEIGHT + BUTTON_GAP), BUTTON_WIDTH, BUTTON_HEIGHT)
btn_credits = pygame.Rect(btn_x, BUTTON_START_Y + 2*(BUTTON_HEIGHT + BUTTON_GAP), BUTTON_WIDTH, BUTTON_HEIGHT)
back_btn = pygame.Rect(20, 440, 80, 30)

# =============================================================================
# BUCLA PRINCIPALĂ A MENIULUI INTRODUCTIV
# =============================================================================

while show_intro:
    # Desenarea fundalului
    screen.fill((0,0,0))
    screen.blit(intro_image, (0,0))

    # Gestionarea evenimentelor
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if intro_state == 'main':
                # Orice tastă pornește jocul (la fel ca butonul Play)
                show_intro = False
            else:
                # În submeniuri, orice tastă revine la meniul principal
                intro_state = 'main'
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if intro_state == 'main':
                # Gestionarea click-urilor pe butoanele principale
                if btn_play.collidepoint((mx,my)):
                    show_intro = False
                elif btn_menu.collidepoint((mx,my)):
                    intro_state = 'menu'
                elif btn_credits.collidepoint((mx,my)):
                    intro_state = 'credits'
            else:
                # În submeniuri, permite click pe butonul Back
                if back_btn.collidepoint((mx,my)):
                    intro_state = 'main'


    # Desenarea conținutului în funcție de starea curentă
    if intro_state == 'main':
        # Desenarea celor trei butoane principale
        draw_button(screen, btn_play, "Play", intro_font, bg=(130, 255, 100))
        draw_button(screen, btn_menu, "Menu", intro_font, bg=(255, 100, 100))
        draw_button(screen, btn_credits, "Credits", intro_font, bg=(130,30,90))
        # Hint pentru utilizator
        hint = font_small.render('Press any key to start or click Play', True, (255,255,255))
        screen.blit(hint, (20, 460))
    elif intro_state == 'menu':
        # Placeholder pentru opțiuni viitoare
        overlay = pygame.Surface((360,300), pygame.SRCALPHA)
        overlay.fill((0,0,0,200))
        screen.blit(overlay, (20,100))
        hdr = font_big.render('Menu', True, (255, 255, 255))
        screen.blit(hdr, (200 - hdr.get_width()//2, 160))
        info = font_med.render('Aici vor fi optiuni de setari.', True, (200,200,200))
        screen.blit(info, (200 - info.get_width()//2, 210))
        draw_button(screen, back_btn, "Back", font_small, bg=(70,70,70))
    elif intro_state == 'credits':
        # Afișarea informațiilor despre creatori
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

    # Actualizarea ecranului și controlul FPS
    pygame.display.update()
    clock.tick(INTRO_FPS)

# =============================================================================
# CONFIGURAȚII CULORI ȘI RESURSE GRAFICE PENTRU JOC
# =============================================================================

# Culori pentru fundal și elemente UI
BACKGROUND_COLOR = (187, 173, 160)  # Culoarea de fundal principală
WHITE, BLACK = (255, 255, 255), (0, 0, 0)  # Culori de bază

# Încărcarea și scalarea imaginii de fundal pentru joc
background_img = load_image_safe(os.path.join(BASE_DIR, "fundal_joc.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
if background_img is None:
    # Creează o imagine de fundal simplă dacă încărcarea eșuează
    background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_img.fill(BACKGROUND_COLOR)


# Culori pentru tiles-uri
EMPTY_COLOR = (205, 193, 180)  # Culoarea pentru celulele goale

# Dicționar cu culori vibrante pentru fiecare valoare de tile
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
    4096: (255, 255, 160),  # galben-alb pal, efect "glow"
    8192: (255, 255, 210)   # alb cald, highlight final
}

def draw_ui_texts(screen, game, music_playing):
    """
    Desenează toate textele UI ale jocului.
    
    Args:
        screen: Suprafața pygame pe care se desenează
        game: Instanța jocului Game2048
        music_playing: Starea muzicii
    """
    texts = [
        (f'High Score: {game.high_score}', (20, 10)),
        (f'Level: {game.current_level}', (20, 80)),
        (f'Move: {game.moves}', (300, 40)),
        (f'Score: {game.score}', (300, 80)),
        (f'Music: {"ON" if music_playing else "OFF"} (M)', (300, 10))
    ]
    for text, pos in texts:
        font = font_music if 'Music' in text else font_med
        screen.blit(font.render(text, True, WHITE), pos)

def draw_overlays(screen, game):
    """
    Desenează overlay-urile pentru mesaje speciale (nivel nou, game over).
    
    Args:
        screen: Suprafața pygame pe care se desenează
        game: Instanța jocului Game2048
    """
    # Mesajul de nivel nou (afișat temporar)
    if pygame.time.get_ticks() < game.level_message_until:
        overlay = pygame.Surface((BOARD_SIZE, 80), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        msg = font_big.render(f'Level {game.current_level}', True, WHITE)
        screen.blit(overlay, (BOARD_X, BOARD_Y + 20))
        screen.blit(msg, (BOARD_X + (BOARD_SIZE - msg.get_width()) // 2, BOARD_Y + 20 + (80 - msg.get_height()) // 2))
    
    # Overlay-ul de Game Over
    if game.game_over:
        overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        screen.blit(overlay, (BOARD_X, BOARD_Y))
        for text, y in [('Game Over!', 230), ('Press R to Restart', 280)]:
            font = font_big if 'Game' in text else font_med
            surf = font.render(text, True, BLACK)
            screen.blit(surf, (200 - surf.get_width()//2, y))

# =============================================================================
# CLASA PRINCIPALĂ PENTRU GESTIONAREA JOCULUI
# =============================================================================

class Game2048:
    """
    Clasa principală care gestionează logica jocului 2048.
    """
    
    def __init__(self):
        """Inițializează jocul cu configurațiile implicite."""
        # Configurații de bază pentru joc
        self.GRID_SIZE = DEFAULT_GRID_SIZE  # Dimensiunea inițială a grid-ului
        self.grid = [[0] * self.GRID_SIZE for _ in range(self.GRID_SIZE)]  # Grid-ul principal
        self.score = 0  # Scorul curent
        self.moves = 0  # Numărul de mutări efectuate
        self.high_score = 0  # Cel mai mare scor obținut
        self.game_over = False  # Starea jocului
        
        # Configurații pentru sistemul de nivele
        self.current_level = 1  # Nivelul curent
        self.LEVEL_TARGETS = {
            1: 128,   # Pentru nivelul 1, trebuie să atingi 128
            2: 1024,  # Pentru nivelul 2, trebuie să atingi 1024
            3: 2048,  # Pentru nivelul 3, trebuie să atingi 2048
            4: 4096,  # Pentru nivelul 4, trebuie să atingi 4096
            5: 8192   # Pentru nivelul 5, trebuie să atingi 8192
        }
        
        # Configurații pentru mesajele de nivel
        self.LEVEL_MESSAGE_DURATION_MS = LEVEL_MESSAGE_DURATION_MS  # Durata afișării mesajului de nivel
        self.level_message_until = 0  # Timestamp până la care se afișează mesajul
        
        # Inițializarea jocului
        self.restart()
    
    def spawn_tile(self, board):
        """
        Adaugă un tile nou (2 sau 4) într-o poziție aleatoare goală pe board.
        
        Args:
            board: Grid-ul jocului (listă 2D)
            
        Returns:
            bool: True dacă s-a adăugat un tile, False dacă nu mai sunt poziții goale
        """
        # Găsește toate pozițiile goale
        empties = [(r, c) for r in range(self.GRID_SIZE) for c in range(self.GRID_SIZE) if board[r][c] == 0]
        if not empties:
            return False
        
        # Alege o poziție aleatoare goală
        r, c = random.choice(empties)
        # Folosește constanta pentru probabilitatea tile-ului 4
        board[r][c] = 4 if random.random() < TILE_SPAWN_PROBABILITY_4 else 2
        return True
    
    def can_move(self, board):
        """
        Verifică dacă mai sunt mutări posibile pe board.
        
        Args:
            board: Grid-ul jocului (listă 2D)
            
        Returns:
            bool: True dacă mai sunt mutări posibile, False dacă jocul s-a terminat
        """
        # Verifică dacă mai sunt celule goale
        has_empty = any(board[r][c] == 0 for r in range(self.GRID_SIZE) for c in range(self.GRID_SIZE))
        
        # Verifică dacă sunt tiles adiacente identice pe orizontală
        has_horizontal_merge = any(board[r][c] == board[r][c+1] for r in range(self.GRID_SIZE) for c in range(self.GRID_SIZE-1))
        
        # Verifică dacă sunt tiles adiacente identice pe verticală
        has_vertical_merge = any(board[r][c] == board[r+1][c] for c in range(self.GRID_SIZE) for r in range(self.GRID_SIZE-1))
        
        return has_empty or has_horizontal_merge or has_vertical_merge
    
    def compress_row_left(self, row):
        """
        Comprimă un rând prin eliminarea zerourilor și păstrarea ordinii.
        
        Args:
            row: Lista de valori din rând
            
        Returns:
            list: Rândul comprimat cu zerourile la sfârșit
        """
        # Elimină zerourile și păstrează ordinea
        new = [v for v in row if v != 0]
        # Adaugă zerourile la sfârșit pentru a menține lungimea
        new += [0] * (len(row) - len(new))
        return new
    
    def merge_row_left(self, row):
        """
        Combină tiles-urile identice din stânga și actualizează scorul.
        
        Args:
            row: Lista de valori din rând
            
        Returns:
            list: Rândul după combinarea tiles-urilor
        """
        row = self.compress_row_left(row)
        merged = [False] * len(row)  # Urmărește care tiles au fost deja combinate
        
        # Combină tiles-urile identice adiacente
        for i in range(len(row) - 1):
            if (row[i] != 0 and row[i] == row[i + 1] and 
                not merged[i] and not merged[i + 1]):
                row[i] *= 2  # Combină tiles-urile
                row[i + 1] = 0  # Elimină al doilea tile
                merged[i] = True  # Marchează că primul tile a fost combinat
                self.score += 1  # Incrementează scorul
        
        return self.compress_row_left(row)
    
    def move_left(self, board):
        """
        Mută toate tiles-urile spre stânga și combină cele identice.
        
        Args:
            board: Grid-ul jocului (listă 2D)
            
        Returns:
            tuple: (new_board, moved) - noul grid și dacă s-a produs o mutare
        """
        moved = False
        new_board = []
        
        # Procesează fiecare rând
        for r in range(self.GRID_SIZE):
            new_row = self.merge_row_left(board[r])
            if new_row != board[r]:  # Verifică dacă rândul s-a schimbat
                moved = True
            new_board.append(new_row)
        
        return new_board, moved
    
    def move_right(self, board):
        """
        Mută toate tiles-urile spre dreapta și combină cele identice.
        Implementat prin inversarea rândurilor, aplicarea move_left și inversarea înapoi.
        
        Args:
            board: Grid-ul jocului (listă 2D)
            
        Returns:
            tuple: (new_board, moved) - noul grid și dacă s-a produs o mutare
        """
        # Inversează fiecare rând, aplică move_left, apoi inversează înapoi
        rev = [list(reversed(row)) for row in board]
        moved_board, moved = self.move_left(rev)
        return [list(reversed(row)) for row in moved_board], moved
    
    def transpose(self, board):
        """
        Transpune grid-ul (schimbă rândurile cu coloanele).
        
        Args:
            board: Grid-ul jocului (listă 2D)
            
        Returns:
            list: Grid-ul transpus
        """
        return [list(row) for row in zip(*board)]
    
    def move_up(self, board):
        """
        Mută toate tiles-urile în sus și combină cele identice.
        Implementat prin transpunerea grid-ului, aplicarea move_left și transpunerea înapoi.
        
        Args:
            board: Grid-ul jocului (listă 2D)
            
        Returns:
            tuple: (new_board, moved) - noul grid și dacă s-a produs o mutare
        """
        t = self.transpose(board)
        moved_board, moved = self.move_left(t)
        return self.transpose(moved_board), moved
    
    def move_down(self, board):
        """
        Mută toate tiles-urile în jos și combină cele identice.
        Implementat prin transpunerea grid-ului, aplicarea move_right și transpunerea înapoi.
        
        Args:
            board: Grid-ul jocului (listă 2D)
            
        Returns:
            tuple: (new_board, moved) - noul grid și dacă s-a produs o mutare
        """
        t = self.transpose(board)
        moved_board, moved = self.move_right(t)
        return self.transpose(moved_board), moved
    
    def restart(self):
        """
        Resetează jocul la starea inițială.
        Resetează grid-ul, scorul, numărul de mutări și adaugă două tiles inițiale.
        """
        self.grid = [[0] * self.GRID_SIZE for _ in range(self.GRID_SIZE)]
        self.score = self.moves = 0
        self.game_over = False
        self.spawn_tile(self.grid)  # Adaugă primul tile
        self.spawn_tile(self.grid)  # Adaugă al doilea tile
    
    def next_level(self):
        """
        Avansează la următorul nivel.
        Mărește dimensiunea grid-ului cu 1 și copiază tiles-urile existente.
        """
        self.current_level += 1
        self.GRID_SIZE += 1
        
        # Creează un nou grid mai mare și copiază tiles-urile existente
        new_grid = [[0] * self.GRID_SIZE for _ in range(self.GRID_SIZE)]
        for r in range(len(self.grid)):
            for c in range(len(self.grid[r])):
                new_grid[r][c] = self.grid[r][c]
        
        self.grid, self.game_over = new_grid, False
        self.spawn_tile(self.grid)  # Adaugă un tile nou pe noul grid
        self.level_message_until = pygame.time.get_ticks() + self.LEVEL_MESSAGE_DURATION_MS

# Inițializarea instanței jocului
game = Game2048()

# Redefinirea fonturilor pentru joc (pentru consistență)
font_small = pygame.font.SysFont(None, 18)
font_med = pygame.font.SysFont(None, 25)
font_big = pygame.font.SysFont(None, 40)
font_music = pygame.font.SysFont(None, 15)  # Font special pentru muzică

# =============================================================================
# CONFIGURAȚII MUZICĂ DE FUNDAL
# =============================================================================

# Inițializarea mixer-ului pentru muzică
pygame.mixer.init(frequency=MUSIC_FREQUENCY, size=-16, channels=MUSIC_CHANNELS, buffer=MUSIC_BUFFER)
music_loaded = load_music_safe(os.path.join(BASE_DIR, "hypnotic_jewels.ogg"))
music_playing = False

if music_loaded:
    pygame.mixer.music.set_volume(MUSIC_VOLUME)  # Volum la 50%
    pygame.mixer.music.play(-1)  # -1 înseamnă loop infinit
    music_playing = True
else:
    print("Muzica nu a putut fi încărcată. Jocul va continua fără muzică.")

def toggle_music():
    """
    Comută starea muzicii de fundal între pornit/oprit.
    """
    global music_playing
    if not music_loaded:
        print("Muzica nu este disponibilă.")
        return
    
    if music_playing:
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()
    music_playing = not music_playing


# =============================================================================
# BUCLA PRINCIPALĂ A JOCULUI
# =============================================================================

while running:
    moved_this_frame = False
    
    # Gestionarea evenimentelor
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not game.game_over:
            if event.key == pygame.K_q:
                running = False  # Ieșire din joc
            elif event.key == pygame.K_r:
                game.restart()  # Restart joc
            elif event.key == pygame.K_m:
                toggle_music()  # Comută muzica
            else:
                # Maparea tastelor de mișcare
                moves_dict = {pygame.K_UP: game.move_up, pygame.K_DOWN: game.move_down, 
                             pygame.K_LEFT: game.move_left, pygame.K_RIGHT: game.move_right}
                if event.key in moves_dict:
                    new_grid, moved = moves_dict[event.key](game.grid)
                    if moved:
                        game.grid, moved_this_frame = new_grid, True
        elif event.type == pygame.KEYDOWN and game.game_over:
            if event.key == pygame.K_r:
                game.restart()  # Restart după game over

    # Logica jocului după o mutare
    if moved_this_frame:
        game.moves += 1  # Incrementează numărul de mutări
        game.spawn_tile(game.grid)  # Adaugă un tile nou
        
        # Verificare progres nivel
        target = game.LEVEL_TARGETS.get(game.current_level)
        if target and any(game.grid[r][c] >= target for r in range(game.GRID_SIZE) for c in range(game.GRID_SIZE)):
            game.next_level()  # Avansează la următorul nivel
    
    # Verificare game over
    if not game.can_move(game.grid):
        game.game_over = True
        if game.score > game.high_score:
            game.high_score = game.score  # Actualizează high score-ul
    


    # =============================================================================
    # DESENAREA INTERFEȚEI GRAFICE
    # =============================================================================
    
    # Desenarea fundalului
    screen.fill(BACKGROUND_COLOR)
    screen.blit(background_img, (0, 0))

    # Desenarea tablei de joc (folosim BOARD_SIZE x BOARD_SIZE ca zonă)
    pygame.draw.rect(screen, WHITE, (BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE), border_radius=10)

    # Calcularea dimensiunii celulelor în funcție de game.GRID_SIZE
    total_padding = CELL_PADDING * (game.GRID_SIZE + 1)
    cell_size = max(10, (BOARD_SIZE - total_padding) // game.GRID_SIZE)

    # Desenarea tiles-urilor
    for r in range(game.GRID_SIZE):
        for c in range(game.GRID_SIZE):
            val = game.grid[r][c]
            x = BOARD_X + CELL_PADDING + c * (cell_size + CELL_PADDING)
            y = BOARD_Y + CELL_PADDING + r * (cell_size + CELL_PADDING)
            tile_rect = pygame.Rect(x, y, cell_size, cell_size)
            
            # Desenează celula cu culoarea corespunzătoare
            pygame.draw.rect(screen, TILE_COLORS.get(val, EMPTY_COLOR), tile_rect, border_radius=5)
            
            # Desenează valoarea tile-ului dacă nu este goală
            if val:
                # Calculează dimensiunea fontului în funcție de dimensiunea celulei
                font_size = max(12, int(cell_size * 0.6) - (len(str(val)) - 1) * 4)
                surf = pygame.font.SysFont(None, font_size, bold=True).render(str(val), True, WHITE)
                screen.blit(surf, surf.get_rect(center=tile_rect.center))

    # Desenarea textelor UI
    draw_ui_texts(screen, game, music_playing)

    # Desenarea overlay-urilor (mesaje speciale)
    draw_overlays(screen, game)

    # Actualizarea ecranului și controlul FPS
    pygame.display.flip()
    clock.tick(FPS)  # FPS pentru o experiență fluidă

# =============================================================================
# FINALIZARE JOC
# =============================================================================

# Închiderea pygame și ieșirea din program
pygame.quit()