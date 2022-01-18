import pygame

from settings import *
from map import collision_walls


# Класс, реализующий персонажа со всеми его качествами
class Player:
    def __init__(self, sprites):
        self.x, self.y = player_pos
        self.sprites = sprites
        self.angle = player_angle
        self.sensitivity = 0.004
        self.side = 50
        self.rect = pygame.Rect(*player_pos, self.side, self.side)
        self.shot = False
        self.player_speed = defalt_player_speed

    # Метод, возвращающий текующие координаты персонажа в игровом мире
    # (с декоратором свойств @propery)
    @property
    def pos(self):
        return self.x, self.y

    # Метод, возвращающий список координат, куда персонажу нельзя ступить
    # (с декоратором свойств @propery)
    @property
    def collision_list(self):
        return collision_walls + [pygame.Rect(*obj.get_sprite_pos, obj.side, obj.side) for obj in
                                  self.sprites.list_of_objects if obj.blocked]

    # Метод, вычисляющий, является ли объект запрещённым для нахождения в нём
    # (с декоратором свойств @propery)
    def detect_collision(self, dx, dy):
        next_rect = self.rect.copy()
        next_rect.move_ip(dx, dy)
        hit_indexes = next_rect.collidelistall(self.collision_list)

        if len(hit_indexes):
            delta_x, delta_y = 0, 0
            for hit_index in hit_indexes:
                hit_rect = self.collision_list[hit_index]
                if dx > 0:
                    delta_x += next_rect.right - hit_rect.left
                else:
                    delta_x += hit_rect.right - next_rect.left
                if dy > 0:
                    delta_y += next_rect.bottom - hit_rect.top
                else:
                    delta_y += hit_rect.bottom - next_rect.top

            if abs(delta_x - delta_y) < 10:
                dx, dy = 0, 0
            elif delta_x > delta_y:
                dy = 0
            elif delta_y > delta_x:
                dx = 0
        self.x += dx
        self.y += dy

    # Метод, организующий совместную работу функций для осуществления передвижения персонажа
    # (с декоратором свойств @propery)
    def movement(self):
        self.keys_control()
        self.mouse_control()
        self.rect.center = self.x, self.y
        self.angle %= DOUBLE_PI

    # Обработка клавиатуры для передижения персонажа
    def keys_control(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return True
        if keys[pygame.K_w]:
            dx = self.player_speed * cos_a
            dy = self.player_speed * sin_a
            self.detect_collision(dx, dy)
        if keys[pygame.K_s]:
            dx = -self.player_speed * cos_a
            dy = -self.player_speed * sin_a
            self.detect_collision(dx, dy)
        if keys[pygame.K_a]:
            dx = self.player_speed * sin_a
            dy = -self.player_speed * cos_a
            self.detect_collision(dx, dy)
        if keys[pygame.K_d]:
            dx = -self.player_speed * sin_a
            dy = self.player_speed * cos_a
            self.detect_collision(dx, dy)
        if keys[pygame.K_LEFT]:
            self.angle -= 0.02
        if keys[pygame.K_RIGHT]:
            self.angle += 0.02

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.shot:
                    self.shot = True

    # Обработка мыши для зменения положения камеры относительно угла 0°
    def mouse_control(self):
        if pygame.mouse.get_focused():
            difference = pygame.mouse.get_pos()[0] - HALF_WIDTH
            pygame.mouse.set_pos((HALF_WIDTH, HALF_HEIGHT))
            self.angle += difference * self.sensitivity

    # Метод для установления скорости персонажа в зависимости от определённых игровых обстоятельств
    def update_speed(self, speed):
        self.player_speed = speed
