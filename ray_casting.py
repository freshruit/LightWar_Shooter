import pygame
from settings import *
from map import world_map


def mapping(a, b):
    return (a // SMOOTHNESS) * SMOOTHNESS, (b // SMOOTHNESS) * SMOOTHNESS


def ray_casting(screen, player_pos, player_angle):
    ox, oy = player_pos
    xm, ym = mapping(ox, oy)
    cursor_angle = player_angle - FIELD_OF_VIEW // 2
    for ray in range(COUNT_RAYS):
        sin_a = math.sin(cursor_angle)
        cos_a = math.cos(cursor_angle)
        sin_a = sin_a if sin_a else 0.000001
        cos_a = cos_a if cos_a else 0.000001

        # Вертикальная визуализация/синхронизация
        x, dx = (xm + SMOOTHNESS, 1) if cos_a >= 0 else (xm, -1)
        for i in range(0, WIDTH, SMOOTHNESS):
            vertical_depth = (x - ox) / cos_a
            y = oy + vertical_depth * sin_a
            if mapping(x + dx, y) in world_map:
                break
            x += dx * SMOOTHNESS

        # Горизонтальная визуализация/синхронизация
        y, dy = (ym + SMOOTHNESS, 1) if sin_a >= 0 else (ym, -1)
        for i in range(0, HEIGHT, SMOOTHNESS):
            horizontal_depth = (y - oy) / sin_a
            x = ox + horizontal_depth * cos_a
            if mapping(x, y + dy) in world_map:
                break
            y += dy * SMOOTHNESS

        # Настройка глубины
        depth = vertical_depth if vertical_depth < horizontal_depth else horizontal_depth
        depth *= math.cos(player_angle - cursor_angle)
        visible_height = REMOTENESS / depth
        color = (255, 255, 255)
        pygame.draw.rect(screen, color, (ray * DISTANCE_SCALE,
                                         HEIGHT // 2 - visible_height // 2,
                                         DISTANCE_SCALE,
                                         visible_height))
        cursor_angle += DIFFERENCE_ANGLE
