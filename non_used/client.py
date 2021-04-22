import asyncio
import json
import pickle
import sys
from random import randint

import pygame
from pygame.locals import *


WIDTH, HEIGHT = 300, 300
UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3


class Ball:
    def __init__(self, x, y, dx=5, dy=5, color=(200, 100, 100), radius=20):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def update(self, keys: pygame.key.get_pressed):
        if keys[UP]:
            self.y -= self.dy
        if keys[DOWN]:
            self.y += self.dy
        if keys[RIGHT]:
            self.x += self.dx
        if keys[LEFT]:
            self.x -= self.dx

        if self.x < 0 or self.x + 2 * self.radius > WIDTH:
            self.dy = -self.dy
        if self.y < 0 or self.y + 2 * self.radius > HEIGHT:
            self.dx = -self.dx


class Balls:
    def __init__(self, balls=None):
        if balls is None:
            balls = []
        self.balls = balls

    def add_ball(self, coords):
        self.balls.append(Ball(*coords))

    def update(self, keys):
        for ball in self.balls:
            ball.update(keys)

    def draw(self, screen):
        for ball in self.balls:
            ball.draw(screen)


# этот класс не нужен пока
class Game:
    def __init__(self):
        pygame.init()
        self.screen = None  # pygame.display.set_mode((WIDTH, HEIGHT), SRCALPHA)
        self.balls = Balls()
        self.running = False
        self.clock = pygame.time.Clock()

    def start_game(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), SRCALPHA)
        self.balls.draw(self.screen)

    def redraw(self):
        self.balls.draw(self.screen)
        pygame.display.flip()

    def update(self, keys):
        self.balls.update(keys)
        self.balls.draw(self.screen)


class ClientProtocol(asyncio.Protocol):
    async def start_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), SRCALPHA)
        self.me = Ball(randint(0, WIDTH - 40), randint(0, HEIGHT - 40))
        self.balls = Balls([self.me])
        self.running = False
        self.clock = pygame.time.Clock()
        self.running = True
        while self.running:
            # self.clock.tick(60)
            await asyncio.sleep(2)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            keys = pygame.key.get_pressed()
            up = keys[K_UP]
            down = keys[K_DOWN]
            left = keys[K_LEFT]
            right = keys[K_RIGHT]
            self.send([up, down, left, right])
            self.screen.fill((240, 240, 240))
            self.balls.draw(self.screen)
            pygame.display.flip()

    def update(self, event):
        if event[0] == "add_ball":
            self.balls.add_ball(event[1])
        if event[0] == "move":
            print(event[1])
            self.balls.update(event[1])

    def to_pickle(self, data):
        return pickle.dumps(data)

    def from_pickle(self, data):
        return pickle.loads(data)

    def connection_made(self, transport):
        self.transport = transport
        print(f'Connected to server.')
        asyncio.create_task(self.start_game())
        event = ["add_ball", [self.me.x, self.me.y]]
        print(event)
        self.send(event)

    def connection_lost(self, exception):
        print(f'Connection with server closed.')

    def data_received(self, data):
        print(f'Data received: {self.from_pickle(data)}')
        self.update(self.from_pickle(data))

    def send(self, message):
        self.transport.write(self.to_pickle(message))
        print(f'Data sent: {message}')


message = [1, 2, 3]
SERVER_PORT = 8080

loop = asyncio.get_event_loop()

coro = loop.create_connection(ClientProtocol, '127.0.0.1', SERVER_PORT)
client = loop.run_until_complete(coro)
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
loop.close()