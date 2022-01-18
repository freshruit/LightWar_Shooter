import pygame
import random
from collections import deque
from numba import int32
from numba.core import types
from numba.typed import Dict

from drawing import load_image
from ray_casting import mapping
from settings import *


# Класс, отвечающий за все спрайты и их свойства, использующий для этого словари
class Sprites(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.sprite_parameters = {
            'sprite_barrel': {
                'sprite': load_image('sprites/barrel/base/0.png'),
                'viewing_angles': None,
                'shift': 1.8,
                'scale': (0.4, 0.4),
                'side': 30,
                'animation': deque([load_image(f'sprites/barrel/animation/{i}.png')
                                    for i in range(12)]),
                'death_animation': deque([load_image(f'sprites/barrel/death/{i}.png')
                                          for i in range(4)]),
                'is_dead': None,
                'dead_shift': 2.6,
                'animation_dist': 800,
                'animation_speed': 10,
                'blocked': True,
                'flag': 'decor',
                'obj_action': []
            },
            'sprite_flame': {
                'sprite': load_image('sprites/flame/base/0.png'),
                'viewing_angles': None,
                'shift': 0.7,
                'scale': (0.6, 0.6),
                'side': 30,
                'animation': deque([load_image(f'sprites/flame/animation/{i}.png')
                                    for i in range(16)]),
                'death_animation': [],
                'is_dead': 'immortal',
                'dead_shift': 1.8,
                'animation_dist': 1800,
                'animation_speed': 5,
                'blocked': None,
                'flag': 'decor',
                'obj_action': []
            },
            'npc_devil': {
                'sprite': [load_image(f'sprites/devil/base/{i}.png')
                           for i in range(8)],
                'viewing_angles': True,
                'shift': 0.0,
                'scale': (1.1, 1.1),
                'side': 50,
                'animation': [],
                'death_animation': deque([load_image(f'sprites/devil/death/{i}.png')
                                          for i in range(6)]),
                'is_dead': None,
                'dead_shift': 0.6,
                'animation_dist': None,
                'animation_speed': 10,
                'blocked': True,
                'flag': 'npc',
                'obj_action': deque([load_image(f'sprites/devil/animation/{i}.png')
                                     for i in range(9)]),
            },
            'sprite_door_v': {
                'sprite': [load_image(f'sprites/doors/door_v/{i}.png')
                           for i in range(16)],
                'viewing_angles': True,
                'shift': 0.1,
                'scale': (2.6, 1.2),
                'side': 100,
                'animation': [],
                'death_animation': [],
                'is_dead': 'immortal',
                'dead_shift': 0,
                'animation_dist': 0,
                'animation_speed': 0,
                'blocked': True,
                'flag': 'door_h',
                'obj_action': []
            },
            'sprite_door_h': {
                'sprite': [load_image(f'sprites/doors/door_h/{i}.png')
                           for i in range(16)],
                'viewing_angles': True,
                'shift': 0.1,
                'scale': (2.6, 1.2),
                'side': 100,
                'animation': [],
                'death_animation': [],
                'is_dead': 'immortal',
                'dead_shift': 0,
                'animation_dist': 0,
                'animation_speed': 0,
                'blocked': True,
                'flag': 'door_v',
                'obj_action': []
            },
            'npc_soldier': {
                'sprite': [load_image(f'sprites/soldier/base/{i}.png')
                           for i in range(8)],
                'viewing_angles': True,
                'shift': 0.8,
                'scale': (0.4, 0.6),
                'side': 30,
                'animation': [],
                'death_animation': deque([load_image(f'sprites/soldier/death/{i}.png')
                                          for i in range(10)]),
                'is_dead': None,
                'dead_shift': 1.7,
                'animation_dist': None,
                'animation_speed': 6,
                'blocked': True,
                'flag': 'npc',
                'obj_action': deque([load_image(f'sprites/soldier/animation/{i}.png')
                                     for i in range(4)])
            },
        }

        self.list_of_objects = [
            SpriteObject(self.sprite_parameters['sprite_door_v'], (3.5, 3.5)),
            SpriteObject(self.sprite_parameters['sprite_door_h'], (1.5, 4.5)),
        ]

    # Установление нужного количства спрайтов в зависимости от сложности уровня (1-5)
    def complication(self, score):
        if score == 6:
            score = 5
        for i in range(score * 4):
            self.list_of_objects.append(SpriteObject(self.sprite_parameters['npc_soldier'],
                                                     (random.uniform(2, 23), random.uniform(2, 15))))
            if i % 2:
                self.list_of_objects.append(SpriteObject(self.sprite_parameters['sprite_flame'],
                                                         (random.uniform(2, 23), random.uniform(2, 15))))
            elif i % 3:
                self.list_of_objects.append(SpriteObject(self.sprite_parameters['npc_devil'],
                                                         (random.uniform(2, 23), random.uniform(2, 15))))
            elif i % 4:
                self.list_of_objects.append(SpriteObject(self.sprite_parameters['sprite_barrel'],
                                                         (random.uniform(2, 23), random.uniform(2, 15))))

    # Метод, проверяющий, пересекается ли луч выстрела с каким-то из спрайтов
    # (с декоратором свойств @propery)
    @property
    def sprite_shot(self):
        return min([obj.is_on_fire for obj in self.list_of_objects], default=(float('inf'), 0))

    # Метод, осуществляющий своевременное открытие и закрытие ворот в игре
    # (с декоратором свойств @propery)
    @property
    def blocked_doors(self):
        blocked_doors = Dict.empty(key_type=types.UniTuple(int32, 2), value_type=int32)
        for obj in self.list_of_objects:
            if obj.flag in {'door_h', 'door_v'} and obj.blocked:
                i, j = mapping(obj.x, obj.y)
                blocked_doors[(i, j)] = 0
        return blocked_doors

    def sprite_pos(self):
        return [sprite.sprite_pos() for sprite in self.list_of_objects]


# Класс, отвечающий за экземпляры классов спрайтов и их правильное взаимодействие с персонажем
class SpriteObject(pygame.sprite.Sprite):
    def __init__(self, parameters, pos, *groups):
        super().__init__(*groups)
        self.zeroing()
        self.groups = groups
        self.n_animation = 0
        self.dead_sprite = 0
        self.proj_height = 0
        self.current_ray = 0
        self.theta = 0
        self.distance_to_sprite = 0
        self.object = parameters['sprite'].copy()
        self.viewing_angles = parameters['viewing_angles']
        self.shift = parameters['shift']
        self.scale = parameters['scale']
        self.animation = parameters['animation'].copy()

        self.death_animation = parameters['death_animation'].copy()
        self.is_dead = parameters['is_dead']
        self.dead_shift = parameters['dead_shift']

        self.animation_dist = parameters['animation_dist']
        self.animation_speed = parameters['animation_speed']
        self.blocked = parameters['blocked']
        self.flag = parameters['flag']
        self.obj_action = parameters['obj_action'].copy()
        self.x, self.y = pos[0] * TILE, pos[1] * TILE
        self.side = parameters['side']
        self.dead_animation_count = 0
        self.animation_count = 0
        self.npc_action_trigger = False
        self.door_open_trigger = False
        self.door_prev_pos = self.y if self.flag == 'door_h' else self.x
        self.delete = False
        if self.viewing_angles:
            if len(self.object) == 8:
                self.sprite_angles = [frozenset(range(338, 361)) | frozenset(range(0, 23))] + \
                                     [frozenset(range(i, i + 45)) for i in range(23, 338, 45)]
            else:
                self.sprite_angles = [frozenset(range(348, 361)) | frozenset(range(0, 11))] + \
                                     [frozenset(range(i, i + 23)) for i in range(11, 348, 23)]
            self.sprite_positions = {angle: pos for angle, pos in zip(self.sprite_angles, self.object)}

    # Очистка экрана по заверешении выстрела
    def zeroing(self):
        global n_shot
        n_shot = 0

    # Проверка, был ли осуществлён выстрел
    @property
    def is_on_fire(self):
        if CENTER_RAY - self.side // 2 < self.current_ray < CENTER_RAY + self.side // 2 and self.blocked:
            return self.distance_to_sprite, self.proj_height
        return float('inf'), None

    # Получение текующих координат конкретного спрайта при определённых обстоятельствах
    @property
    def get_sprite_pos(self):
        return self.x - self.side // 2, self.y - self.side // 2

    # Установление положения спрайта в игровом мире
    def object_locate(self, player):
        dx, dy = self.x - player.x, self.y - player.y
        self.distance_to_sprite = math.sqrt(dx ** 2 + dy ** 2)
        self.theta = math.atan2(dy, dx)
        gamma = self.theta - player.angle
        if dx > 0 and 180 <= math.degrees(player.angle) <= 360 or dx < 0 and dy < 0:
            gamma += DOUBLE_PI
        self.theta -= 1.4 * gamma
        delta_rays = int(gamma / DELTA_ANGLE)
        self.current_ray = CENTER_RAY + delta_rays
        if self.flag not in {'door_h', 'door_v'}:
            self.distance_to_sprite *= math.cos(HALF_FOV - self.current_ray * DELTA_ANGLE)
        fake_ray = self.current_ray + FAKE_RAYS
        if 0 <= fake_ray <= FAKE_RAYS_RANGE and self.distance_to_sprite > 30:
            self.proj_height = min(int(PROJ_COEFF / self.distance_to_sprite),
                                   DOUBLE_HEIGHT if self.flag not in {'door_h', 'door_v'} else HEIGHT)
            sprite_width = int(self.proj_height * self.scale[0])
            sprite_height = int(self.proj_height * self.scale[1])
            half_sprite_width = sprite_width // 2
            half_sprite_height = sprite_height // 2
            shift = half_sprite_height * self.shift
            if self.flag in {'door_h', 'door_v'}:
                if self.door_open_trigger:
                    self.open_door()
                self.object = self.visible_sprite()
                sprite_object = self.sprite_animation()
            else:
                if self.is_dead and self.is_dead != 'immortal':
                    sprite_object = self.dead_animation()
                    shift = half_sprite_height * self.dead_shift
                    sprite_height = int(sprite_height / 1.3)
                elif self.npc_action_trigger:
                    sprite_object = self.npc_in_action()
                else:
                    self.object = self.visible_sprite()
                    sprite_object = self.sprite_animation()
            sprite_pos = (self.current_ray * SCALE - half_sprite_width, HALF_HEIGHT - half_sprite_height + shift)
            sprite = pygame.transform.scale(sprite_object, (sprite_width, sprite_height))
            return self.distance_to_sprite, sprite, sprite_pos
        else:
            return False,

    # Осуществление анимации спрайтов
    def sprite_animation(self):
        if self.animation and self.distance_to_sprite < self.animation_dist:
            sprite_object = self.animation[0]
            if self.animation_count < self.animation_speed:
                self.animation_count += 1
            else:
                self.animation.rotate()
                self.animation_count = 0
            return sprite_object
        return self.object

    # Проверка, виден ли пользователю спрайт (от этого зависит здоровье персонажа)
    def visible_sprite(self):
        if self.viewing_angles:
            if self.theta < 0:
                self.theta += DOUBLE_PI
            self.theta = 360 - int(math.degrees(self.theta))
            for angles in self.sprite_angles:
                if self.theta in angles:
                    return self.sprite_positions[angles]
        return self.object

    def dead_animation(self):
        if len(self.death_animation):
            if self.dead_animation_count < self.animation_speed:
                self.dead_sprite = self.death_animation[0]
                self.dead_animation_count += 1
            else:
                self.dead_sprite = self.death_animation.popleft()
                self.dead_animation_count = 0
        return self.dead_sprite

    # Определение типа спрайта и его возвращение
    def npc_in_action(self):
        global n_shot
        sprite_object = self.obj_action[0]
        if self.animation_count < self.animation_speed:
            self.animation_count += 1
        else:
            if '92x' == str(sprite_object)[9:12] or '100' == str(sprite_object)[9:12]:
                n_shot += random.random() * damage_per_shot

            self.obj_action.rotate()
            self.animation_count = 0
        return sprite_object

    # Проверка, можно ли открыть дверь игровых ворот
    def open_door(self):
        if self.flag == 'door_h':
            self.y -= 3
            if abs(self.y - self.door_prev_pos) > TILE:
                self.delete = True
        elif self.flag == 'door_v':
            self.x -= 3
            if abs(self.x - self.door_prev_pos) > TILE:
                self.delete = True

    # Возвращение начальной позиции конкретного спрайта
    def sprite_pos(self):
        return self.x, self.y


# Получение информации о том, что выстрел был произведён
def make_shot():
    global n_shot
    return n_shot
