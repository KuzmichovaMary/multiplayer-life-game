import pygame
from network import Client

import sys
import pygame
from life import Life
from config import *
import pickle


def read_data(data):
    print(data, "HERE")
    data = data[1:-1].split()
    command = data[0]
    args = []
    for arg in data[1:]:
        if ":" not in arg:
            args.append(arg)
        else:
            d_type, value = arg.split(":")
            if d_type == "int":
                args.append(int(value))
            else:
                args.append(value)
    return command, args


class Player:
    def __init__(self, cell_color, num_cells=20):
        self.cell_color = cell_color


class Game:
    def __init__(self, network, color, pattern_file=None):
        self.life = Life()
        self.screen = None
        self.scale = START_SCALE
        self.base_x, self.base_y = None, None
        if pattern_file:
            self.life.load(pattern_file)
        self.paused = False
        self.running = False
        self.clock = None
        self.network = network
        self.color = color

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
        received = self.network.send("(get_alive )", res=True)
        print(received)
        alive = pickle.loads(received)
        self.life.alive = alive
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
                data = f"(toggle int:{x} int:{y} int:{self.color})"
                self.network.send(data)
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

# width = 600
# height = 600
# win = pygame.display.set_mode((width, height))
# pygame.display.set_caption("Client")
#
# clientNumber = 0
#
#
# class Player:
#     def __init__(self, x, y, width, height, color):
#         self.x = x
#         self.y = y
#         self.width = width
#         self.height = height
#         self.color = color
#         self.rect = (x, y, width, height)
#         self.vel = 3
#
#     def draw(self, win):
#         pygame.draw.rect(win, self.color, self.rect)
#
#     def move(self):
#         keys = pygame.key.get_pressed()
#
#         if keys[pygame.K_LEFT]:
#             self.x -= self.vel
#         if keys[pygame.K_RIGHT]:
#             self.x += self.vel
#         if keys[pygame.K_UP]:
#             self.y -= self.vel
#         if keys[pygame.K_DOWN]:
#             self.y += self.vel
#
#         self.update()
#
#     def update(self):
#         self.rect = (self.x, self.y, self.width, self.height)
#
#
# def readPos(str):
#     str = str.split(",")
#     return int(str[0]), int(str[1])
#
#
# def makePos(tup):
#     return str(tup[0]) + "," + str(tup[1])
#
#
# def redrawWindow(win, player, player2):
#     win.fill((255, 255, 255))
#
#     player.draw(win)
#     player2.draw(win)
#
#     pygame.display.update()


# def main():
#     n = Network()
#     color = read_data(n.send(b"(get color )"))
#     game = Game(n, color)
#
#     clock = pygame.time.Clock()
#
#     run = True
#     while run:
#         clock.tick(60)
#
#         p2Pos = readPos(n.send(makePos((p.x, p.y))))
#         p2.x = p2Pos[0]
#         p2.y = p2Pos[1]
#         p2.update()
#
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False
#
#         p.move()
#         redrawWindow(win, p, p2)
#
#     pygame.quit()


def main_1():
    n = Client()
    print("starting game")
    game = Game(n, read_data(n.color)[1][0])
    game.start_game()

    while game.running:
        game.clock.tick(FPS)
        game.update()
        game.draw()

    pygame.quit()


main_1()
