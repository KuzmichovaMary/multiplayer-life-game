import pygame
from network import Client

import sys
import pygame
from life import Life
from config import *
import pickle


SECONDS_IN_MINUTE = 60
MINUTE = 1


def ms_to_minutes(time_in_milliseconds):
    return time_in_milliseconds / 1000 / 60


def ms_to_seconds(time_in_milliseconds):
    return time_in_milliseconds / 1000


def read_data(data):
    """read data in format
        (command data_type:value data_type:value ...)
        >>>read_data("(toggle int:1 int:2 str:alpha")"""
    print(data, "HERE")
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
        self.placing_cells_mode = True
        self.placing_cells_mode_time = 2 * MINUTE
        self.rounds = 5
        self.round_generations = 50
        self.curr_round_generations = 0
        self.show_round_info_time = 30  # seconds
        self.c = 0

    def center(self):
        cell_count_h = HEIGHT // self.scale
        cell_count_w = WIDTH // self.scale
        minx, miny, maxx, maxy = self.life.bounding_box()

        self.base_x = minx - (cell_count_w - (maxx - minx + 1)) // 2
        self.base_y = miny - (cell_count_h - (maxy - miny + 1)) // 2

    def start_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), SRCALPHA)
        pygame.display.set_caption(f'Game of Life (placing time)')
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
        # elif event.unicode == ' ':
        #     self.paused = not self.paused
        #     if self.paused:
        #         pygame.display.set_caption('Game of Life (paused)')
        #     else:
        #         pygame.display.set_caption(
        #             f'Game of Life [{self.life.rules_str()}]')
        elif event.key == K_EQUALS:
            if self.scale < MAX_SCALE:
                self.scale += SCALE_DELTA
        elif event.key == K_MINUS:
            if self.scale > MIN_SCALE:
                self.scale -= SCALE_DELTA
        elif event.unicode == 'c':
            self.center()

    def update(self, event=None):
        # event_type = event[0]
        # self.on(event_type)
        if self.placing_cells_mode:
            received = self.network.send("(get_alive )", res=True)
            alive = pickle.loads(received)
            self.life.alive = alive
            cmd, args = read_data(self.network.send(f"(start_eating? int:{self.color - 1})", res=True).decode())
            if cmd == "yes":
                self.placing_cells_mode = False
                pygame.display.set_caption("Life (eating phase)")

        else:
            self.life.advance()
            # print(self.network.send("(start_new_round? )", res=True))
            raw_data = self.network.send(f"(start_new_round? int:{self.color - 1})", res=True)
            if raw_data:
                cmd, args = read_data(raw_data.decode())
            else:
                cmd, args = None, [None]
            # print(cmd)
            self.c += 1
            if cmd == "yes":
                self.placing_cells_mode = True
                start_time = ms_to_seconds(pygame.time.get_ticks())
                self.screen.fill(NEW_ROUND_BACKGROUND)
                while ms_to_seconds(pygame.time.get_ticks()) - start_time < self.show_round_info_time:
                    self.draw_new_round()
                    pygame.display.flip()
                self.start_new_round()
                pygame.display.set_caption("Life (placing time)")

        pygame_events = pygame.event.get(EVENT_TYPES)
        for event in pygame_events:
            pygame_event_type = event.type
            if pygame_event_type == QUIT:
                pygame.quit()
                sys.exit()
            elif self.placing_cells_mode and pygame_event_type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                x = mouse_x // self.scale + self.base_x
                y = mouse_y // self.scale + self.base_y
                data = f"(toggle int:{x} int:{y} int:{self.color})"
                self.network.send(data)
            elif pygame_event_type == KEYDOWN:
                self.on_key_down(event)

    def draw(self):
        self.screen.fill(WHITE)
        for x in range(0, WIDTH, self.scale):  # draw vertical lines
            pygame.draw.line(self.screen, BLACK, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, self.scale):  # draw horizontal lines
            pygame.draw.line(self.screen, BLACK, (0, y), (WIDTH, y))
        for x, y in self.life.alive:  # draw live cells
            pygame.draw.rect(self.screen, COLORS[self.life.alive.getitem((y, x))],
                             ((x - self.base_x) * self.scale + GRID_LINE_WIDTH + CELL_MARGIN,
                              (y - self.base_y) * self.scale + GRID_LINE_WIDTH + CELL_MARGIN,
                              self.scale - GRID_LINE_WIDTH - 2 * CELL_MARGIN,
                              self.scale - GRID_LINE_WIDTH - 2 * CELL_MARGIN))

        pygame.display.flip()

    def display_text(self, text, y, font_size=50, pos="middle", x=10, width=WIDTH):
        font = pygame.font.Font(None, font_size)
        text = font.render(text, True, (0, 0, 0, 100))
        text_width = text.get_rect().w
        if pos == "middle":
            self.screen.blit(text, (width / 2 - text_width / 2, y))
        else:
            self.screen.blit(text, (x, y))

    def display_lines(self, y, lines, font_size=40):
        for ind, line in enumerate(lines):
            self.display_text(line, y + ind * font_size, font_size)

    def draw_new_round(self):
        score = 9
        lines = [
            "Rounded ended."
            f"Your score {score}."
        ]
        self.display_lines(10, lines)

    def start_new_round(self):
        self.life = Life()

    def main(self):
        while True:
            self.clock.tick(FPS)
            self.update()
            self.draw()


if __name__ == '__main__':
    network = Client()
    print("Starting game")
    game = Game(network, read_data(network.color)[1][0])
    game.start_game()
