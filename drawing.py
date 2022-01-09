import pygame
import random
import sys
import os
from collections import *

import player_processing
from settings import *
from map import mini_map

pygame.init()
screen = pygame.display.set_mode(SIZE)
screen_map = pygame.Surface(MINIMAP_RES)
pygame.display.set_caption('Light War')


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


class Drawing:
    def __init__(self, screen, screen_map, player, clock):
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

    def background(self, angle):
        sky_offset = -10 * math.degrees(angle) % WIDTH
        self.screen.blit(self.textures['S'], (sky_offset, 0))
        self.screen.blit(self.textures['S'], (sky_offset - WIDTH, 0))
        self.screen.blit(self.textures['S'], (sky_offset + WIDTH, 0))
        pygame.draw.rect(self.screen, DARKGRAY, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))

    def world(self, world_objects):
        for obj in sorted(world_objects, key=lambda n: n[0], reverse=True):
            if obj[0]:
                _, object, object_pos = obj
                self.screen.blit(object, object_pos)

    def fps(self, clock):
        display_fps = str(int(clock.get_fps()))
        render = self.fps_font.render(f"FPS:{display_fps}", False, DARKORANGE)
        self.screen.blit(render, FPS_POS)

    def mini_map(self, player):
        self.screen_map.fill(BLACK)
        map_x, map_y = player.x // MAP_SCALE, player.y // MAP_SCALE
        pygame.draw.line(self.screen_map, YELLOW, (map_x, map_y),
                         (map_x + 12 * math.cos(player.angle),
                          map_y + 12 * math.sin(player.angle)), 2)
        pygame.draw.circle(self.screen_map, RED, (int(map_x), int(map_y)), 5)
        for x, y in mini_map:
            pygame.draw.rect(self.screen_map, SANDY, (x, y, MAP_TILE, MAP_TILE))
        self.screen.blit(self.screen_map, MAP_POS)

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

    def bullet_sfx(self):
        if self.sfx_length_count < self.sfx_length:
            sfx = pygame.transform.scale(self.sfx[0], (self.shot_projection, self.shot_projection))
            sfx_rect = sfx.get_rect()
            self.screen.blit(sfx, (HALF_WIDTH - sfx_rect.w // 2, HALF_HEIGHT - sfx_rect.h // 2))
            self.sfx_length_count += 1
            self.sfx.rotate(-1)

    def win(self):
        button_font = pygame.font.Font('data/fonts/pixel_font.ttf', 72)

        render = self.font_win.render('Победа!', True, (random.randrange(40, 120), 0, 0))
        rect = pygame.Rect(0, 0, 1000, 300)
        rect.center = HALF_WIDTH, HALF_HEIGHT
        pygame.draw.rect(self.screen, BLACK, rect, border_radius=50)
        self.screen.blit(render, (rect.centerx - 330, rect.centery - 140))

        menu = button_font.render('Меню', True, pygame.Color('lightgray'))
        button_menu = pygame.Rect(0, 0, 370, 111)
        button_menu.center = HALF_WIDTH - 250, HALF_HEIGHT + 250

        exit = button_font.render('Выйти', True, pygame.Color('lightgray'))
        button_exit = pygame.Rect(0, 0, 370, 111)
        button_exit.center = HALF_WIDTH + 250, HALF_HEIGHT + 250

        self.menu_trigger = True
        while self.menu_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.draw.rect(self.screen, BLACK, button_menu, border_radius=25, width=10)
            self.screen.blit(menu, (button_menu.centerx - 120, button_menu.centery - 75))

            pygame.draw.rect(self.screen, BLACK, button_exit, border_radius=25, width=10)
            self.screen.blit(exit, (button_exit.centerx - 130, button_exit.centery - 75))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            pygame.mouse.set_visible(True)
            if button_menu.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_menu, border_radius=25)
                self.screen.blit(menu, (button_menu.centerx - 120, button_menu.centery - 75))
                if mouse_click[0]:
                    return True
            elif button_exit.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_exit, border_radius=25)
                self.screen.blit(exit, (button_exit.centerx - 130, button_exit.centery - 75))
                if mouse_click[0]:
                    pygame.quit()
                    sys.exit()
            pygame.display.flip()
            self.clock.tick(15)

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
                    elif event.key == pygame.K_RETURN:
                        screen.fill((0, 0, 0))
                        return name

            text = self.font.render(name, True, (0, 0, 0))
            description = self.font.render("Введите никнейм", True, (0, 0, 0))
            developers = self.font.render("Ganzha & Medvedev company", True, (0, 0, 0))
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
            screen.blit(developers, (900, 750))
            screen.blit(description, (x, y))
            if text_w <= 300:
                pygame.draw.rect(screen, (0, 0, 0), (430, text_y - 10,
                                                     300, text_h + 20), 3)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (text_x - 10, text_y - 10,
                                                     text_w + 20, text_h + 20), 3)
            pygame.display.update()
        pygame.quit()

    def menu(self):
        x = 0
        button_font = pygame.font.Font('data/fonts/pixel_font.ttf', 72)
        label_font = pygame.font.Font('data/fonts/cyberpunk_font.ttf', 168)

        start = button_font.render('Играть', True, pygame.Color('lightgray'))
        button_start = pygame.Rect(0, 0, 370, 111)
        button_start.center = HALF_WIDTH, HALF_HEIGHT - 50

        exit = button_font.render('Выйти', True, pygame.Color('lightgray'))
        button_exit = pygame.Rect(0, 0, 370, 111)
        button_exit.center = HALF_WIDTH, HALF_HEIGHT + 250

        leaders = button_font.render('Лидеры', True, pygame.Color('lightgray'))
        button_leaders = pygame.Rect(0, 0, 370, 111)
        button_leaders.center = HALF_WIDTH, HALF_HEIGHT + 100

        while self.menu_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            color = random.randrange(40)
            self.screen.blit(self.menu_picture, (0, 0), (x % WIDTH, HALF_HEIGHT, WIDTH, HEIGHT))
            x += 1

            pygame.draw.rect(self.screen, BLACK, button_start, border_radius=25, width=10)
            self.screen.blit(start, (button_start.centerx - 140, button_start.centery - 75))

            pygame.draw.rect(self.screen, BLACK, button_exit, border_radius=25, width=10)
            self.screen.blit(exit, (button_exit.centerx - 130, button_exit.centery - 75))

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
            elif button_exit.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_exit, border_radius=25)
                self.screen.blit(exit, (button_exit.centerx - 130, button_exit.centery - 75))
                if mouse_click[0]:
                    pygame.quit()
                    sys.exit()
            elif button_leaders.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLACK, button_leaders, border_radius=25)
                self.screen.blit(leaders, (button_leaders.centerx - 170, button_leaders.centery - 75))
                if mouse_click[0]:
                    pass
            pygame.display.flip()
            self.clock.tick(20)
