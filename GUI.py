import sys
import os

import pygame
from config import *


SPACE = 10
TOP_SLIDER_SPACE = 40
SPACE_BEETWEN_SLIDERS = 20


def load_image(name, colorkey=None):
    fullname = os.path.join('', name)
    if not os.path.isfile(fullname):
        print(f"Image '{fullname}' not found.")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


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
            left = self.x + self.circle_x - self.circle_radius + 20
            right = self.circle_x + self.circle_radius + self.x + 20
            top = self.y_ + 20
            bottom = self.y + self.h / 2 + self.circle_radius + 20
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
                         (self.circle_radius, max(0, self.circle_radius - self.h / 2), self.w - 2 * self.circle_radius, self.h),
                         border_radius=2)
        pygame.draw.circle(self.surface, self.circle_color, (self.circle_x, self.circle_radius), self.circle_radius)
        screen.blit(self.surface, self.rect)

    def get_value(self):
        uno = (self.w - 2 * self.circle_radius) / (self.max - self.min)
        value = (self.circle_x - self.circle_radius) / uno
        if value > self.max:
            return self.max
        if value < self.min:
            return self.min
        return value


class ButtonBase:
    def __init__(self, x, y, job_on_click, active=True, color=(255, 200, 10, 0), icon_path_1="", icon_path_2=""):
        self.default_image = load_image(icon_path_1)
        self.clicked_image = load_image(icon_path_2)
        self.image = self.default_image
        self.rect = pygame.Rect(0, 0, self.image.get_rect().w, self.image.get_rect().h).move(x, y)
        self.color = color
        self.icon_path_1 = icon_path_1
        self.icon_path_2 = icon_path_2
        self.clicked = False
        self.job = job_on_click
        self.active = active
        self.images = [self.default_image, self.clicked_image]
        self.curr_index = 0

    def update(self):
        if self.active:
            mouse_on_widget = self.rect.collidepoint(pygame.mouse.get_pos())
            if mouse_on_widget:
                self.clicked = True
                self.change_icon()
                self.job()

    def display(self, screen):
        screen.blit(self.image, self.rect)

    def change_icon(self):
        pass


class Button(ButtonBase):
    def change_icon(self):
        self.curr_index = abs(self.curr_index - 1)
        self.image = self.images[self.curr_index]


class ColorPicker:
    def __init__(self, x, y, w, h, job_on_set):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.job_on_set = job_on_set
        self.slider_w = min(h, int((self.w - SPACE) / 2))
        self.slider_h = 6
        self.surface = pygame.Surface((w, h), SRCALPHA)
        self.rect = pygame.Rect(x, y, w, h)
        self.current_color = (0, 0, 0)
        
        self.top_slider_space = (h - 3 * self.slider_h - 2 * SPACE_BEETWEN_SLIDERS) / 2
        self.top_color_rect_space = (h - self.slider_w) / 2

        self.set_button = Button(self.slider_w / 2 - 20, self.top_slider_space + 3 * self.slider_h + 3 * SPACE_BEETWEN_SLIDERS, job_on_click=job_on_set, icon_path_1="chevrons-right.png", icon_path_2="chevrons-right.png")


        self.R_slider = Slider(0, self.top_slider_space, self.slider_w, self.slider_h)
        self.G_slider = Slider(0, self.top_slider_space + SPACE_BEETWEN_SLIDERS + self.slider_h,
                               self.slider_w, self.slider_h)
        self.B_slider = Slider(0, self.top_slider_space + 2 * self.slider_h + 2 * SPACE_BEETWEN_SLIDERS,
                               self.slider_w, self.slider_h)
        self.r, self.g, self.b = 0, 0, 0

    def display(self, screen):
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.surface, (200, 200, 200, 220),
                         (0, 0, self.w, self.h), border_radius=5)
        self.R_slider.display(self.surface)
        self.G_slider.display(self.surface)
        self.B_slider.display(self.surface)
        self.r = self.R_slider.get_value()
        self.g = self.G_slider.get_value()
        self.b = self.B_slider.get_value()
        pygame.draw.rect(self.surface, (self.r, self.g, self.b), (SPACE + self.slider_w, self.top_color_rect_space, self.slider_w, self.slider_w),
            border_radius=2)
        self._display_rgb()
        self.set_button.display(self.surface)
        screen.blit(self.surface, self.rect)

    def update(self, event_type):
        self.R_slider.update(event_type)
        self.G_slider.update(event_type)
        self.B_slider.update(event_type)
        if event_type == MOUSEBUTTONDOWN:
            self.set_button.update()

    def _display_rgb(self):
        font = pygame.font.Font(None, 30)
        text = font.render(f"R: {int(self.r)} G: {int(self.g)} B: {int(self.b)}", True, (0, 0, 0, 100))
        y = self.top_color_rect_space + ((self.top_slider_space - self.top_color_rect_space) / 2 - 7)
        self.surface.blit(text, (SPACE, y))



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


