import pygame
from numba import int32
from numba.core import types
from numba.typed import Dict

from settings import *

world_map = Dict.empty(key_type=types.UniTuple(int32, 2), value_type=int32)
mini_map = set()
collision_walls = []
map = None
WORLD_WIDTH = 0
WORLD_HEIGHT = 0


def create_map():
    global WORLD_WIDTH, WORLD_HEIGHT, map
    with open("data/levels/1.txt") as level:
        map = [[int(i) for i in row if i != '\n'] for row in level]
        WORLD_WIDTH = len(map[0]) * TILE
        WORLD_HEIGHT = len(map) * TILE
        for j, row in enumerate(map):
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
