import sys

import pygame
from config import *


SPACE = 10
TOP_SLIDER_SPACE = 40
SPACE_BEETWEN_SLIDERS = 20


class Slider:
    def __init__(self, x, y, w, h, circle_radius=10, circle_color=(200, 100, 100), back_color=GRAY, min_=0, max_=255):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.circle_radius = circle_radius
        self.circle_color = circle_color
        self.back_color = back_color
        self.circle_x = self.circle_radius
        add_ = 2 * circle_radius - h
        print(w, h, (w, h + add_))
        self.surface = pygame.Surface((w, h + add_), SRCALPHA)
        self.rect = pygame.Rect(x, y - (circle_radius - h / 2), w, h + add_)
        self.mouse_pressed = False
        self.y_ = y - (circle_radius - h / 2)
        self.min = min_
        self.max = max_

    def mouse_pos_to_surf_coords(self, m_x, m_y):
        return m_x - self.x, m_y - self.y_

    def update(self, event_type):
        m_x, m_y = pygame.mouse.get_pos()
        if event_type == MOUSEBUTTONDOWN:
            left = self.x + self.circle_x - self.circle_radius
            right = self.circle_x + self.circle_radius + self.x
            top = self.y_
            bottom = self.y + self.h / 2 + self.circle_radius
            if left <= m_x <= right and top <= m_y <= bottom:
                self.mouse_pressed = True
        if event_type == MOUSEMOTION and self.mouse_pressed:
            if m_x > self.w - self.circle_radius:
                self.circle_x = self.w - self.circle_radius
            elif m_x < self.circle_radius:
                self.circle_x = self.circle_radius
            else:
                self.circle_x = m_x
        if event_type == MOUSEBUTTONUP:
            self.mouse_pressed = False

    def display(self, screen):
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.surface, self.back_color,
                         (self.circle_radius, max(0, self.circle_radius - self.h / 2), self.w - 2 * self.circle_radius, self.h))
        pygame.draw.circle(self.surface, self.circle_color, (self.circle_x, self.circle_radius), self.circle_radius)
        screen.blit(self.surface, self.rect)

    def get_value(self):
        uno = self.w / (self.max - self.min)
        value = (self.circle_x - self.circle_radius) / uno
        if value > self.max:
            return self.max
        if value < self.min:
            return self.min
        return value


class ColorPicker:
    def __init__(self, x, y, w):
        self.x = x
        self.y = y
        self.w = w
        self.slider_w = int((self.w - 3 * SPACE) / 2)
        self.slider_h = 6
        m = self.slider_w - 3 * self.slider_h
        self.surface = pygame.Surface((w, h), SRCALPHA)
        self.rect = pygame.Rect(x, y, w, h)
        self.current_color = (0, 0, 0)

        self.R_slider = Slider(SPACE, TOP_SLIDER_SPACE, self.slider_w, self.slider_h)
        self.G_slider = Slider(SPACE, TOP_SLIDER_SPACE + SPACE_BEETWEN_SLIDERS + self.slider_h,
                               self.slider_w, self.slider_h)
        self.B_slider = Slider(SPACE, TOP_SLIDER_SPACE + 2 * self.slider_h + 2 * SPACE_BEETWEN_SLIDERS,
                               self.slider_w, self.slider_h)

    def display(self, screen):
        self.surface.fill((0, 0, 0, 0))
        self.R_slider.display(self.surface)
        self.G_slider.display(self.surface)
        self.B_slider.display(self.surface)
        r = self.R_slider.get_value()
        g = self.G_slider.get_value()
        b = self.B_slider.get_value()
        pygame.draw.rect(self.surface, (r, g, b), (2 * SPACE + self.slider_w, SPACE, self.slider_w, self.slider_w))
        screen.blit(self.surface, self.rect)

    def update(self, event_type):
        self.R_slider.update(event_type)
        self.G_slider.update(event_type)
        self.B_slider.update(event_type)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((400, 300), SRCALPHA)
    clock = pygame.time.Clock()
    cp = ColorPicker(0, 0, 400, 300)

    while True:
        for event in pygame.event.get():
            event_type = event.type
            cp.update(event_type)
            if event_type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(60)
        screen.fill((255, 255, 255))
        cp.display(screen)
        #pygame.draw.circle(screen, (255, 0, 0), pygame.mouse.get_pos(), 5)
        pygame.display.flip()


