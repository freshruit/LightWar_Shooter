import pygame
import random
import sys
from settings import *


class user_hp:
    def __init__(self, screen):
        self.screen = screen
        self.condition_dead = False

    def apdate_hp(self, n_shot):
        n_hp = amount_user_hp - int(n_shot)
        len_one_hp = position_hp[2] // amount_user_hp - 1

        pygame.draw.rect(self.screen, (0, 0, 0),
                         position_hp)
        if n_hp > 0:
            for i in range(n_hp):
                pygame.draw.rect(self.screen, (255, 0, 0),
                                 ((len_one_hp + 1) * i + position_hp[0], position_hp[1], len_one_hp, position_hp[3]))
        else:
            self.condition_dead = True

        pygame.draw.rect(self.screen, (255, 255, 255),
                         position_hp, 1)

    def check_dead(self):
        if self.condition_dead:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('data/sounds/win.mp3')
            pygame.mixer.music.play()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                return True

