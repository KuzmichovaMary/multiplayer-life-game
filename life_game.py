import sys
import pygame
from life import Life
from config import *


class Player:
    def __init__(self, cell_color, num_cells=20):
        self.cell_color = cell_color


class Game:
    def __init__(self, pattern_file=None):
        self.life = Life()
        self.screen = None
        self.scale = START_SCALE
        self.base_x, self.base_y = None, None
        if pattern_file:
            self.life.load(pattern_file)
        self.paused = False
        self.running = False
        self.clock = None

    def center(self):
        cell_count_h = HEIGHT // self.scale
        cell_count_w = WIDTH // self.scale
        minx, miny, maxx, maxy = self.life.bounding_box()

        self.base_x = minx - (cell_count_w - (maxx - minx + 1)) // 2
        self.base_y = miny - (cell_count_h - (maxy - miny + 1)) // 2

    def start_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), SRCALPHA)
        pygame.display.set_caption(f'Game of Life [{self.life.rules_str()}]')
        self.center()
        self.clock = pygame.time.Clock()
        self.running = True

    def on(self, event_type, data):
        pass

    def update(self, event=None):
        # event_type = event[0]
        # self.on(event_type)
        if not self.paused:
            self.life.advance()

        pygame_events = pygame.event.get(EVENT_TYPES)
        for event in pygame_events:
            pygame_event_type = event.type
            if pygame_event_type == QUIT or not self.running:
                pygame.quit()
                sys.exit()
            elif pygame_event_type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                x = mouse_x // self.scale + self.base_x
                y = mouse_y // self.scale + self.base_y
                data = ["toggle", x, y]
                self.life.toggle(x, y)
            elif pygame_event_type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_LEFT:
                    self.base_x -= SCROLL_DELTA
                elif event.key == K_RIGHT:
                    self.base_x += SCROLL_DELTA
                elif event.key == K_UP:
                    self.base_y -= SCROLL_DELTA
                elif event.key == K_DOWN:
                    self.base_y += SCROLL_DELTA
                elif event.unicode == ' ':
                    self.paused = not self.paused
                    if self.paused:
                        pygame.display.set_caption('Game of Life (paused)')
                    else:
                        pygame.display.set_caption(
                            f'Game of Life [{self.life.rules_str()}]')
                elif event.key == K_EQUALS:
                    if self.scale < MAX_SCALE:
                        self.scale += SCALE_DELTA
                elif event.key == K_MINUS:
                    if self.scale > MIN_SCALE:
                        self.scale -= SCALE_DELTA
                elif event.unicode == 'c':
                    self.center()

    def draw(self):
        self.screen.fill(WHITE)
        for x in range(0, WIDTH, self.scale):
            pygame.draw.line(self.screen, BLACK, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, self.scale):
            pygame.draw.line(self.screen, BLACK, (0, y), (WIDTH, y))
        for x, y in self.life.alive:
            pygame.draw.rect(self.screen, COLORS[self.life.alive.getitem((y, x))],
                             ((x - self.base_x) * self.scale + GRID_LINE_WIDTH + CELL_MARGIN,
                              (y - self.base_y) * self.scale + GRID_LINE_WIDTH + CELL_MARGIN,
                              self.scale - GRID_LINE_WIDTH - 2 * CELL_MARGIN,
                              self.scale - GRID_LINE_WIDTH - 2 * CELL_MARGIN))

        pygame.display.flip()


if __name__ == '__main__':
    def game_loop():
        game = Game()
        game.start_game()

        while game.running:
            game.clock.tick(FPS)
            game.draw()
            game.update()
    print('''
Press: Arrows to scroll
       Space to pause/resume the simulation
       +/- to zoom in/out
       c to re-center
       mouse click to toggle the state of a cell
       Esc to exit''')
    game_loop()
    pygame.quit()