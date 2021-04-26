import pygame
from network import Client

import sys
import pygame
from life import Life
from config import *
import pickle
import os


pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)


def read_data(data):
    """read data in format
        (command data_type:value data_type:value ...)
        >>>read_data("(toggle int:1 int:2 str:alpha")
        >>>("toggle", 1, 2, "alpha")"""
    # print(data, "HERE")
    if not data:
        return None, [None]
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


class Note:
    def __init__(self, x, y, w, h, lines=None, color=NEW_ROUND_BACKGROUND):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text_lines = lines
        self.color = color
        self.display_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.display_rect = pygame.Rect(x, y, w, h)

    def display_color_text_middle(self, text, y, color, font_size=32, width=WIDTH):
        color_block_w = font_size - 2
        font = pygame.font.Font(None, font_size)
        text = font.render(text, True, (0, 0, 0, 100))
        x = None
        if x is None:
            text_width = text.get_rect().w + color_block_w + COLOR_TEXT_SPACE
            x = width / 2 - text_width / 2
        pygame.draw.rect(self.display_surface, color,
                         (x, y, color_block_w - 6, color_block_w - 6), border_radius=5)
        self.display_surface.blit(text, (x + color_block_w + COLOR_TEXT_SPACE, y))

    def display_lines(self, y, lines, font_size=32, height=HEIGHT):
        for ind, pair in enumerate(lines):
            # print(pair)
            line, color = pair
            if not color:
                self.display_color_text_middle(line, y + ind * font_size + 2, NEW_ROUND_BACKGROUND, font_size)
            else:
                self.display_color_text_middle(line, y + ind * font_size + 2, COLORS[color], font_size)

    def display(self, screen, lines):
        self.display_surface.fill((90, 90, 90, 0))
        pygame.draw.rect(self.display_surface, self.color,
                         (0, 0, self.w, self.h), border_radius=NEW_ROUND_MESSAGE_BORDER_RADIUS)
        self.display_lines(NEW_ROUND_TEXT_TOP, lines)
        screen.blit(self.display_surface, self.display_rect)


class Game:
    def __init__(self, network, color):
        self.screen = None
        self.scale = START_SCALE
        self.base_x, self.base_y = None, None
        self.paused = False
        self.running = False
        self.clock = None
        self.network = network
        self.color_id = color
        self.c = 0

        self.placing_cells_mode = True
        self.showing_info_mode = False
        self.eating_mode = False

        self.w, self.h = None, None
        self.alive = None
        self.new_round_info = Note(15, 15, WIDTH - 30, HEIGHT - 30)
        self.scores = None

        self.caption = "Life game"
        self.captions = {
            "eat": "Eating time",
            "place_cells": "Placing cells time",
            "show_info": ""
        }

        self.watching_settings = False

    def center(self):
        cell_count_h = HEIGHT // self.scale
        cell_count_w = WIDTH // self.scale
        received = self.network.send("(bounding_box )", res=True)
        min_x, min_y, max_x, max_y = pickle.loads(received)

        self.base_x = min_x - (cell_count_w - (max_x - min_x + 1)) // 2
        self.base_y = min_y - (cell_count_h - (max_y - min_y + 1)) // 2

    def start_game(self):
        pygame.init()
        self.screen = SCREEN
        pygame.display.set_caption(f'Game of Life')
        self.center()
        self.clock = pygame.time.Clock()
        self.main()

    def on_key_down(self, event):
        key = event.key
        if key == K_ESCAPE:
            self.running = False
        elif key == K_LEFT:
            self.base_x -= SCROLL_DELTA
        elif key == K_RIGHT:
            self.base_x += SCROLL_DELTA
        elif key == K_UP:
            self.base_y -= SCROLL_DELTA
        elif key == K_DOWN:
            self.base_y += SCROLL_DELTA
        elif event.key == K_EQUALS:
            if self.scale < MAX_SCALE:
                self.scale += SCALE_DELTA
        elif event.key == K_MINUS:
            if self.scale > MIN_SCALE:
                self.scale -= SCALE_DELTA
        elif event.unicode == 'c':
            self.center()

    def on_mouse_buttondown(self):
        if self.placing_cells_mode:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            x = mouse_x // self.scale + self.base_x
            y = mouse_y // self.scale + self.base_y
            data = f"(toggle int:{x} int:{y} int:{self.color_id})"
            self.network.send(data)

    def set_caption(self, cmd):
        if self.caption != self.captions[cmd]:
            self.caption = self.captions[cmd]
            pygame.display.set_caption(self.caption)

    def change_mode(self, cmd):
        if cmd == "show_info":
            self.showing_info_mode = True
            self.placing_cells_mode = False
            self.eating_mode = False
        elif cmd == "eat":
            pygame.display.set_caption("eating")
            self.eating_mode = True
            self.placing_cells_mode = False
            self.showing_info_mode = False
        elif cmd == "place_cells":
            pygame.display.set_caption("placing")
            self.placing_cells_mode = True
            self.showing_info_mode = False
            self.eating_mode = False

    def update(self):
        cmd = self.network.send(f"(what_now? int:{self.color_id})", res=True).decode()
        self.set_caption(cmd)
        self.change_mode(cmd)

        if self.placing_cells_mode:
            received = self.network.send("(get_alive )", res=True)
            self.alive = pickle.loads(received)
        elif self.eating_mode:
            received = self.network.send("(advance )", res=True)
            self.alive = pickle.loads(received)
        elif self.showing_info_mode:
            received = self.network.send(f"(get_scores )", res=True)
            # print(received)
            self.scores = pickle.loads(received)
            pygame.display.set_caption("Life (placing time)")

        pygame_events = pygame.event.get(EVENT_TYPES)
        for event in pygame_events:
            pygame_event_type = event.type
            if pygame_event_type == QUIT:
                pygame.quit()
                sys.exit()
            elif pygame_event_type == MOUSEBUTTONDOWN:
                self.on_mouse_buttondown()
            elif pygame_event_type == KEYDOWN:
                self.on_key_down(event)

    def draw(self):
        if self.showing_info_mode:
            self.draw_cells()
            self.draw_new_round()
        else:
            self.draw_cells()
        pygame.display.flip()

    def draw_cells(self):
        self.screen.fill(WHITE)
        for x in range(0, WIDTH, self.scale):  # draw vertical lines
            pygame.draw.line(self.screen, BLACK, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, self.scale):  # draw horizontal lines
            pygame.draw.line(self.screen, BLACK, (0, y), (WIDTH, y))
        for x, y in self.alive:  # draw live cells
            pygame.draw.rect(self.screen, COLORS[self.alive.getitem((y, x))],
                             ((x - self.base_x) * self.scale + GRID_LINE_WIDTH + CELL_MARGIN,
                              (y - self.base_y) * self.scale + GRID_LINE_WIDTH + CELL_MARGIN,
                              self.scale - GRID_LINE_WIDTH - 2 * CELL_MARGIN,
                              self.scale - GRID_LINE_WIDTH - 2 * CELL_MARGIN))

    def draw_new_round(self):
        # print(scores)
        scoreboard = list(sorted(list(self.scores.items()), key=lambda x: x[1]))
        lines = [
            ("Round ended.", None),
        ]
        for color_id, score in scoreboard:
            lines.append((f" - {score}", color_id))
        self.new_round_info.display(self.screen, lines)

    def main(self):
        while True:
            self.clock.tick(FPS)
            self.update()
            self.draw()


if __name__ == '__main__':
    network = Client()
    # print("Starting game")
    game = Game(network, read_data(network.color)[1][0])
    game.start_game()
