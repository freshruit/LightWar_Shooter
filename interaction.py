import pygame
import sys
import time
from numba import njit

from settings import *
from ray_casting import mapping
from map import world_map

total_time = 0


# Проекция лучей от камеры к случайной точке движущихся спрайтов
@njit(fastmath=True, cache=True)
def ray_casting_npc_player(npc_x, npc_y, blocked_doors, world_map, player_pos):
    ox, oy = player_pos
    xm, ym = mapping(ox, oy)
    delta_x, delta_y = ox - npc_x, oy - npc_y
    cur_angle = math.atan2(delta_y, delta_x)
    cur_angle += math.pi

    sin_a = math.sin(cur_angle)
    sin_a = sin_a if sin_a else 0.000001
    cos_a = math.cos(cur_angle)
    cos_a = cos_a if cos_a else 0.000001

    # Вертикальная виртуализация интерактивных спрайтов
    x, dx = (xm + TILE, 1) if cos_a >= 0 else (xm, -1)
    for i in range(0, int(abs(delta_x)) // TILE):
        depth_v = (x - ox) / cos_a
        yv = oy + depth_v * sin_a
        tile_v = mapping(x + dx, yv)
        if tile_v in world_map or tile_v in blocked_doors:
            return False
        x += dx * TILE

    # Горизонтальная виртуализация интерактивных спрайтов
    y, dy = (ym + TILE, 1) if sin_a >= 0 else (ym, -1)
    for i in range(0, int(abs(delta_y)) // TILE):
        depth_h = (y - oy) / sin_a
        xh = ox + depth_h * cos_a
        tile_h = mapping(xh, y + dy)
        if tile_h in world_map or tile_h in blocked_doors:
            return False
        y += dy * TILE
    return True


# Функция для проигрывания фоновой музыки
def play_music():
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    pygame.mixer.music.load('data/sounds/theme.mp3')
    pygame.mixer.music.play(10)


# Класс, реализующий взаимодействие игрока со всеми спрайтами
class Interaction:
    def __init__(self, player, sprites, drawing, screen):
        self.old_time = 0
        self.n_adversary = 0
        self.flag_time = True
        self.font = pygame.font.SysFont('Arial', 20, bold=True)
        self.player = player
        self.sprites = sprites
        self.drawing = drawing
        self.screen = screen
        self.win_flag = False
        self.flag_adversary = True
        self.pain_sound = pygame.mixer.Sound('data/sounds/pain.mp3')

    # Метод, проверяющий, к какому классу отнести спрайт
    def interaction_objects(self):
        if self.player.shot and self.drawing.shot_animation_trigger:
            for obj in sorted(self.sprites.list_of_objects, key=lambda obj: obj.distance_to_sprite):
                if obj.is_on_fire[1]:
                    if obj.is_dead != 'immortal' and not obj.is_dead:
                        if ray_casting_npc_player(obj.x, obj.y,
                                                  self.sprites.blocked_doors,
                                                  world_map, self.player.pos):
                            if obj.flag == 'npc':
                                self.pain_sound.play()
                            obj.is_dead = True
                            obj.blocked = None
                            self.drawing.shot_animation_trigger = False
                    if obj.flag in {'door_h', 'door_v'} and obj.distance_to_sprite < TILE:
                        obj.door_open_trigger = True
                        obj.blocked = None
                    break

    # Метод, проверяющий, можно ли двигаться в направлении, запрашиваемом игроком
    def npc_action(self):
        for obj in self.sprites.list_of_objects:
            if obj.flag == 'npc' and not obj.is_dead:
                if ray_casting_npc_player(obj.x, obj.y,
                                          self.sprites.blocked_doors,
                                          world_map, self.player.pos):
                    obj.npc_action_trigger = True
                    self.npc_move(obj)
                else:
                    obj.npc_action_trigger = False

    # Осуществление перемещения спрайтов в сторону игрока
    def npc_move(self, obj):
        if abs(obj.distance_to_sprite) > TILE:
            dx = obj.x - self.player.pos[0]
            dy = obj.y - self.player.pos[1]
            obj.x = obj.x + 1 if dx < 0 else obj.x - 1
            obj.y = obj.y + 1 if dy < 0 else obj.y - 1

    # Очистка мира для загрузки следующего уровня
    def clear_world(self):
        deleted_objects = self.sprites.list_of_objects[:]
        [self.sprites.list_of_objects.remove(obj) for obj in deleted_objects if obj.delete]

    # Проверка, все ли спрайты уничтожены (возможно ли завершить игру)
    def check_win(self):
        global total_time
        count_living_sprites = len([obj for obj in self.sprites.list_of_objects
                                    if obj.flag == 'npc' and not obj.is_dead])
        if self.flag_adversary:
            self.n_adversary = count_living_sprites
            self.flag_adversary = False
        render_adversary = self.font.render(f"Осталось противников:{str(count_living_sprites)}/{str(self.n_adversary)}",
                                            False, DARKORANGE)
        self.screen.blit(render_adversary, (0, 166))

        if self.flag_time:
            self.old_time = round(time.time())
            self.flag_time = False

        total_time = round(time.time()) - self.old_time
        render_time = self.font.render(f"Время прохождения:{total_time} сек.",
                                       False, DARKORANGE)
        self.screen.blit(render_time, (0, 186))

        if not count_living_sprites:
            self.win_flag = True
            pygame.mixer.music.stop()
            pygame.mixer.music.load('data/sounds/win.mp3')
            pygame.mixer.music.play()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                return True
