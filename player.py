import pygame
from settings import *


class Player:
    def __init__(self):
        self.x, self.y = player_position
        self.angle = player_angle
        self.sensitivity = 0.004

    @property
    def position(self):
        return self.x, self.y

    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        key = pygame.key.get_pressed()
        if key[pygame.K_w]:
            self.x += player_speed * cos_a
            self.y += player_speed * sin_a
        if key[pygame.K_a]:
            self.x += player_speed * sin_a
            self.y += -player_speed * cos_a
        if key[pygame.K_s]:
            self.x += -player_speed * cos_a
            self.y += -player_speed * sin_a
        if key[pygame.K_d]:
            self.x += -player_speed * sin_a
            self.y += player_speed * cos_a
        if key[pygame.K_LEFT]:
            self.angle -= 0.02
        if key[pygame.K_RIGHT]:
            self.angle += 0.02
        if pygame.mouse.get_focused():
            difference = pygame.mouse.get_pos()[0] - WIDTH // 2
            pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))
            self.angle += difference * self.sensitivity
