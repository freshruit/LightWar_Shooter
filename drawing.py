import pygame
from settings import *
from ray_casting import ray_casting
from map import mini_map


class Drawing:
    def __init__(self, screen, screen_map):
        self.screen = screen
        self.screen_map = screen_map
        self.font = pygame.font.SysFont('Times New Roman', 36, bold=True)

    def draw_background(self):
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, WIDTH, HEIGHT // 2))
        pygame.draw.rect(self.screen, (0, 0, 0), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

    def visualize_world(self, player_position, player_angle):
        ray_casting(self.screen, player_position, player_angle)

    def display_fps(self, clock):
        display_fps = str(int(clock.get_fps()))
        render = self.font.render(display_fps, False, (255, 0, 0))
        self.screen.blit(render, FPS_COUNTER_POSITION)

    def make_min_map(self, player):
        self.screen_map.fill((0, 0, 0))
        map_x, map_y = player.x // MAP_SCALE, player.y // MAP_SCALE
        pygame.draw.line(self.screen_map,
                         (255, 255, 255),
                         (map_x, map_y),
                         (map_x + 12 * math.cos(player.angle),
                          map_y + 12 * math.sin(player.angle)),
                         2)
        pygame.draw.circle(self.screen_map,
                           (255, 0, 255),
                           (int(map_x),
                            int(map_y)),
                           5)
        for x, y in mini_map:
            pygame.draw.rect(self.screen_map,
                             (255, 255, 255),
                             (x, y, MAP_SMOOTHNESS, MAP_SMOOTHNESS))
        self.screen.blit(self.screen_map, MAP_POSITION)
