import pygame
from numba import int32
from numba.core import types
from numba.typed import Dict

from settings import *

world_map = Dict.empty(key_type=types.UniTuple(int32, 2), value_type=int32)
mini_map = set()
collision_walls = []
matrix_map = None
WORLD_WIDTH = 0
WORLD_HEIGHT = 0


def create_map(score):
    if score == 6:
        score = 5
    global WORLD_WIDTH, WORLD_HEIGHT, matrix_map
    with open(f"data/levels/{score}.txt") as level:
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
