from pygame.locals import *


EVENT_TYPES = [QUIT, KEYDOWN, MOUSEBUTTONDOWN]
WIDTH, HEIGHT = 300, 300
CELL_MARGIN = 5

GREISH_BLUE = (80, 80, 192)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SEA_BLUE = (100, 200, 200)
RED = (240, 10, 10)
NEW_ROUND_BACKGROUND = (58, 202, 187, 200)

COLORS = {
    1: GREISH_BLUE,
    2: SEA_BLUE,
    3: RED
}

START_SCALE = 20
SCROLL_DELTA = 2
SCALE_DELTA = 5
MIN_SCALE, MAX_SCALE = 10, 50

GRID_LINE_WIDTH = 1
FPS = 10
INTERVAL = 1000 / FPS