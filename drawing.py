import pygame
import random
import sqlite3
import sys
import os
from collections import *

import player_processing
from settings import *
from map import mini_map

# Инициализация pygame
pygame.init()
screen = pygame.display.set_mode(SIZE)
screen_map = pygame.Surface(MINIMAP_RES)
pygame.display.set_caption('Light War')


# Функция загрузки изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
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


# Функция парсинга базы данных
def data_leaderboard():
    con = sqlite3.connect('data/LightWar.db')
    cur = con.cursor()
    data = cur.execute("""
                           SELECT * FROM users WHERE highscore = ? ORDER BY time DESC
                       """, (6,)).fetchall()
    con.commit()
    con.close()
    return data[::-1][:3]


# Класс, реализующий отрисовку всех объектов в игре
class Drawing:
    def __init__(self, screen, screen_map, player, clock, sprites):
        self.sprites = sprites
        self.x = 0
        self.shot_projection = 0
        self.screen = screen
        self.screen_map = screen_map
        self.player = player
        self.clock = clock
        self.fps_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_win = pygame.font.Font('data/fonts/pixel_font.ttf', 144)
        self.textures = {1: load_image('textures/wall1.jpg'),
                         2: load_image('textures/wall2.jpg'),
                         3: load_image('textures/wall3.jpg'),
                         4: load_image('textures/wall4.jpg'),
                         'S': load_image('textures/sky.jpg')
                         }
        self.menu_trigger = True
        self.menu_picture = load_image('textures/background.jpg')
        self.weapon_base_sprite = load_image('sprites/weapons/shotgun/base/0.png')
        self.weapon_shot_animation = deque([load_image(f'sprites/weapons/shotgun/shot/{i}.png')
                                            for i in range(20)])
        self.weapon_rect = self.weapon_base_sprite.get_rect()
        self.weapon_pos = (HALF_WIDTH - self.weapon_rect.width // 2, HEIGHT - self.weapon_rect.height)
        self.shot_length = len(self.weapon_shot_animation)
        self.shot_length_count = 0
        self.shot_animation_speed = 3
        self.shot_animation_count = 0
        self.shot_animation_trigger = True
        self.shot_sound = pygame.mixer.Sound('data/sounds/shotgun.mp3')
        self.sfx = deque([load_image(f'sprites/weapons/sfx/{i}.png') for i in range(9)])
        self.sfx_length_count = 0
        self.sfx_length = len(self.sfx)
        self.font = pygame.font.SysFont('Arial', 20, bold=True)

    # Загрузка фонового изображения
    def background(self, angle):
        sky_offset = -10 * math.degrees(angle) % WIDTH
        self.screen.blit(self.textures['S'], (sky_offset, 0))
        self.screen.blit(self.textures['S'], (sky_offset - WIDTH, 0))
        self.screen.blit(self.textures['S'], (sky_offset + WIDTH, 0))
        pygame.draw.rect(self.screen, DARKGRAY, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))

    # Проекция игрового мира, реализуемого в файле ray_casting, на экран пользователя
    def world(self, world_objects):
        for obj in sorted(world_objects, key=lambda n: n[0], reverse=True):
            if obj[0]:
                _, object, object_pos = obj
                self.screen.blit(object, object_pos)

    # Отображение fps в углу экрана
    def fps(self, clock):
        display_fps = str(int(clock.get_fps()))
        render = self.fps_font.render(f"FPS:{display_fps}", False, DARKORANGE)
        self.screen.blit(render, FPS_POS)

    # Надпись "Здоровье" под счётчиком здоровья
    def health(self):
        render = self.fps_font.render("Здоровье", False, RED)
        self.screen.blit(render, (250, 30))

    # "Склейка" мини-карты с игровым миром
    def mini_map(self, player):
        cords_living_sprites = ([obj.sprite_pos() for obj in self.sprites.list_of_objects
                                 if obj.flag == 'npc' and not obj.is_dead])

        self.screen_map.fill(BLACK)
        map_x, map_y = player.x // MAP_SCALE, player.y // MAP_SCALE
        pygame.draw.line(self.screen_map, YELLOW, (map_x, map_y),
                         (map_x + 12 * math.cos(player.angle),
                          map_y + 12 * math.sin(player.angle)), 2)

        pygame.draw.circle(self.screen_map, GREEN, (int(map_x), int(map_y)), 5)

        for x, y in mini_map:
            pygame.draw.rect(self.screen_map, SANDY, (x, y, MAP_TILE, MAP_TILE))
        for spr_cords_x, spr_cords_y in cords_living_sprites:
            pygame.draw.circle(self.screen_map, RED, (spr_cords_x // MAP_SCALE,
                                                      spr_cords_y // MAP_SCALE), 5)
        self.screen.blit(self.screen_map, MAP_POS)

    # Нанесение оружие на экран пользователя
    def player_weapon(self, shots):
        if self.player.shot:
            if not self.shot_length_count:
                self.shot_sound.play()
            self.shot_projection = min(shots)[1] // 2
            self.bullet_sfx()
            shot_sprite = self.weapon_shot_animation[0]
            self.screen.blit(shot_sprite, self.weapon_pos)
            self.shot_animation_count += 1
            if self.shot_animation_count == self.shot_animation_speed:
                self.weapon_shot_animation.rotate(-1)
                self.shot_animation_count = 0
                self.shot_length_count += 1
                self.shot_animation_trigger = False
            if self.shot_length_count == self.shot_length:
                self.player.shot = False
                self.shot_length_count = 0
                self.sfx_length_count = 0
                self.shot_animation_trigger = True
        else:
            self.screen.blit(self.weapon_base_sprite, self.weapon_pos)

    # Разметка места выстрела пользователем
    def bullet_sfx(self):
        if self.sfx_length_count < self.sfx_length:
            sfx = pygame.transform.scale(self.sfx[0], (self.shot_projection, self.shot_projection))
            sfx_rect = sfx.get_rect()
            self.screen.blit(sfx, (HALF_WIDTH - sfx_rect.w // 2, HALF_HEIGHT - sfx_rect.h // 2))
            self.sfx_length_count += 1
            self.sfx.rotate(-1)

    # Метод для выведения сообщения о победе или поражения пользователя
    def win_or_dead_message(self, condition_life):
        button_font = pygame.font.Font('data/fonts/pixel_font.ttf', 72)

        render = self.font_win.render(('Победа!' if condition_life else 'Поражение!'), True,
                                      (random.randrange(40, 120), 0, 0))
        rect = pygame.Rect(0, 0, (1000 if condition_life else 1200), 300)
        rect.center = HALF_WIDTH, HALF_HEIGHT
        pygame.draw.rect(self.screen, BLACK, rect, border_radius=50)
        self.screen.blit(render, (rect.centerx - (330 if condition_life else 500), rect.centery - 140))

        menu = button_font.render('Меню', True, pygame.Color('lightgray'))
        button_menu = pygame.Rect(0, 0, 370, 111)
        button_menu.center = HALF_WIDTH - 250, HALF_HEIGHT + 250

        leave = button_font.render('Выйти', True, pygame.Color('lightgray'))
        button_leave = pygame.Rect(0, 0, 370, 111)
        button_leave.center = HALF_WIDTH + 250, HALF_HEIGHT + 250

        self.menu_trigger = True
        while self.menu_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.draw.rect(self.screen, BLACK, button_menu, border_radius=25, width=10)
            self.screen.blit(menu, (button_menu.centerx - 120, button_menu.centery - 75))

            pygame.draw.rect(self.screen, BLACK, button_leave, border_radius=25, width=10)
            self.screen.blit(leave, (button_leave.centerx - 130, button_leave.centery - 75))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            pygame.mouse.set_visible(True)
            if button_menu.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_menu, border_radius=25)
                self.screen.blit(menu, (button_menu.centerx - 120, button_menu.centery - 75))
                if mouse_click[0]:
                    return True
            elif button_leave.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_leave, border_radius=25)
                self.screen.blit(leave, (button_leave.centerx - 130, button_leave.centery - 75))
                if mouse_click[0]:
                    pygame.quit()
                    sys.exit()
            pygame.display.flip()
            self.clock.tick(15)

    # Метод для ввода никнейма перед загрузкой меню
    def enter_name(self):
        image = load_image('textures/background.jpg')
        name = ""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        name += "a"
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.key == pygame.K_b:
                        name += "b"
                    elif event.key == pygame.K_c:
                        name += "c"
                    elif event.key == pygame.K_d:
                        name += "d"
                    elif event.key == pygame.K_e:
                        name += "e"
                    elif event.key == pygame.K_f:
                        name += "f"
                    elif event.key == pygame.K_j:
                        name += "j"
                    elif event.key == pygame.K_k:
                        name += "k"
                    elif event.key == pygame.K_l:
                        name += "l"
                    elif event.key == pygame.K_g:
                        name += "g"
                    elif event.key == pygame.K_m:
                        name += "m"
                    elif event.key == pygame.K_n:
                        name += "n"
                    elif event.key == pygame.K_o:
                        name += "o"
                    elif event.key == pygame.K_p:
                        name += "p"
                    elif event.key == pygame.K_q:
                        name += "q"
                    elif event.key == pygame.K_r:
                        name += "r"
                    elif event.key == pygame.K_s:
                        name += "s"
                    elif event.key == pygame.K_t:
                        name += "t"
                    elif event.key == pygame.K_u:
                        name += "u"
                    elif event.key == pygame.K_w:
                        name += "w"
                    elif event.key == pygame.K_h:
                        name += "h"
                    elif event.key == pygame.K_x:
                        name += "x"
                    elif event.key == pygame.K_y:
                        name += "y"
                    elif event.key == pygame.K_z:
                        name += "z"
                    elif event.key == pygame.K_SPACE:
                        name += " "
                    elif event.key == pygame.K_v:
                        name += "v"
                    elif event.key == pygame.K_i:
                        name += "i"
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_RETURN:
                        screen.fill((0, 0, 0))
                        return name

            text = self.font.render(name, True, (0, 0, 0))
            description = self.font.render("Введите никнейм", True, (0, 0, 0))
            developers = self.font.render("Ganzha & Medvedev production", True, (0, 0, 0))
            x = 500
            y = 350
            text_x = 525
            text_y = 400
            text_w = text.get_width()
            text_h = text.get_height()
            screen.fill((0, 0, 0))
            image1 = pygame.transform.scale(image, (1200, 800))
            screen.blit(image1, (0, 0))
            screen.blit(text, (text_x, text_y))
            screen.blit(developers, (850, 750))
            screen.blit(description, (x, y))
            if text_w <= 300:
                pygame.draw.rect(screen, (0, 0, 0), (430, text_y - 10,
                                                     300, text_h + 20), 3)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (text_x - 10, text_y - 10,
                                                     text_w + 20, text_h + 20), 3)
            pygame.display.update()
        pygame.quit()

    # Функция для виртуализации меню
    def menu(self):
        self.x = 0
        button_font = pygame.font.Font('data/fonts/pixel_font.ttf', 72)
        label_font = pygame.font.Font('data/fonts/cyberpunk_font.ttf', 168)

        start = button_font.render('Играть', True, pygame.Color('lightgray'))
        button_start = pygame.Rect(0, 0, 370, 111)
        button_start.center = HALF_WIDTH, HALF_HEIGHT - 50

        leave = button_font.render('Выйти', True, pygame.Color('lightgray'))
        button_leave = pygame.Rect(0, 0, 370, 111)
        button_leave.center = HALF_WIDTH, HALF_HEIGHT + 250

        leaders = button_font.render('Лидеры', True, pygame.Color('lightgray'))
        button_leaders = pygame.Rect(0, 0, 370, 111)
        button_leaders.center = HALF_WIDTH, HALF_HEIGHT + 100

        while self.menu_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            color = random.randrange(40)
            self.screen.blit(self.menu_picture, (0, 0), (self.x % WIDTH, HALF_HEIGHT, WIDTH, HEIGHT))
            self.x += 1

            pygame.draw.rect(self.screen, BLACK, button_start, border_radius=25, width=10)
            self.screen.blit(start, (button_start.centerx - 140, button_start.centery - 75))

            pygame.draw.rect(self.screen, BLACK, button_leave, border_radius=25, width=10)
            self.screen.blit(leave, (button_leave.centerx - 130, button_leave.centery - 75))

            pygame.draw.rect(self.screen, BLACK, button_leaders, border_radius=25, width=10)
            self.screen.blit(leaders, (button_leaders.centerx - 170, button_leaders.centery - 75))

            label = label_font.render('LightWar', True, (color, color, color))
            self.screen.blit(label, (100, 50))

            if player_processing.total_highscore == 6:
                highscore = "Игра завершена!"
            else:
                highscore = player_processing.total_highscore

            label = self.fps_font.render(f"Текущий уровень: {highscore}", True,
                                         (color, color, color))
            self.screen.blit(label, (120, 20))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            pygame.mouse.set_visible(True)
            if button_start.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_start, border_radius=25)
                self.screen.blit(start, (button_start.centerx - 140, button_start.centery - 75))
                if mouse_click[0]:
                    pygame.mouse.set_visible(False)
                    self.menu_trigger = False
            elif button_leave.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_leave, border_radius=25)
                self.screen.blit(leave, (button_leave.centerx - 130, button_leave.centery - 75))
                if mouse_click[0]:
                    pygame.quit()
                    sys.exit()
            elif button_leaders.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_leaders, border_radius=25)
                self.screen.blit(leaders, (button_leaders.centerx - 170, button_leaders.centery - 75))
                if mouse_click[0]:
                    self.make_leaderboard()
            pygame.display.flip()
            self.clock.tick(20)

    # Метод для виртуализации таблицы лидеров при нажатии кнопки "Лидеры" в главном меню
    def make_leaderboard(self):
        button_font = pygame.font.Font('data/fonts/pixel_font.ttf', 72)
        label_font = pygame.font.Font('data/fonts/cyberpunk_font.ttf', 168)

        back = button_font.render('Назад', True, pygame.Color('lightgray'))
        button_back = pygame.Rect(0, 0, 370, 111)
        button_back.center = HALF_WIDTH + 400, HALF_HEIGHT + 333

        self.menu_trigger = True
        while self.menu_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            color = random.randrange(40)
            self.screen.blit(self.menu_picture, (0, 0), (self.x % WIDTH, HALF_HEIGHT, WIDTH, HEIGHT))
            self.x += 1

            pygame.draw.rect(self.screen, BLACK, button_back, border_radius=25, width=10)
            self.screen.blit(back, (button_back.centerx - 140, button_back.centery - 75))

            label = label_font.render('LightWar', True, (color, color, color))
            self.screen.blit(label, (100, 50))

            warning = self.font.render("В таблицу лидеров попадают игроки, прошедшие 5-ый уровень!",
                                       True, (0, 0, 0))
            self.screen.blit(warning, (350, 270))

            leaders = self.font.render("ID Никнейм Затраченное время(сек)", True, (0, 0, 0))
            self.screen.blit(leaders, (350, 300))

            for j, row in enumerate(data_leaderboard()):
                user_id, name, level, time = row

                label_id = self.font.render(str(user_id), True, (0, 0, 0))
                screen.blit(label_id, (345, 350 + j * 50))

                label_name = self.font.render(name, True, (0, 0, 0))
                screen.blit(label_name, (375, 350 + j * 50))

                label_time = self.font.render(str(time), True, (0, 0, 0))
                screen.blit(label_time, (525, 350 + j * 50))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            pygame.mouse.set_visible(True)
            if button_back.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_back, border_radius=25)
                self.screen.blit(back, (button_back.centerx - 140, button_back.centery - 75))
                if mouse_click[0]:
                    return True
            pygame.display.flip()
            self.clock.tick(15)
