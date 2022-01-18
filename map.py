import pygame
from numba import int32
from numba.core import types
from numba.typed import Dict

from settings import *

# Генерация карты как словаря, где ключами являются координаты,
# а значениями массивы из данных о каждой точке игрового мира
world_map = Dict.empty(key_type=types.UniTuple(int32, 2), value_type=int32)

# Проекция игрового мира сверху вниз в виде мини-карты в левом верхнем углу экрана
mini_map = set()

# Запись координат, на которые персонаж физически не сможет ступить (стены)
collision_walls = []

# Открытие файла уровня и проход по нему
with open("data/levels/map.txt") as level:
    matrix_map = [[int(i) for i in row if i != '\n'] for row in level]
    WORLD_WIDTH = len(matrix_map[0]) * TILE
    WORLD_HEIGHT = len(matrix_map) * TILE
    for j, row in enumerate(matrix_map):
        for i, char in enumerate(row):
            if char:
                mini_map.add((i * MAP_TILE, j * MAP_TILE))
                collision_walls.append(pygame.Rect(i * TILE, j * TILE, TILE, TILE))
                if char == 1:
                    world_map[(i * TILE, j * TILE)] = 1
                elif char == 2:
                    world_map[(i * TILE, j * TILE)] = 2
                elif char == 3:
                    world_map[(i * TILE, j * TILE)] = 3
                elif char == 4:
                    world_map[(i * TILE, j * TILE)] = 4
