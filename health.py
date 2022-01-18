import pygame
import sys

from settings import *


# Функция для расчёта здоровья персонажа
def calculate_hp(n_level):
    global amount_user_hp
    if n_level == 1:
        amount_user_hp = 20
    if n_level == 2:
        amount_user_hp = 30
    if n_level == 3:
        amount_user_hp = 40
    if n_level == 4:
        amount_user_hp = 50
    if n_level == 5:
        amount_user_hp = 60


# Класс для изменения здоровья персонажа на экране пользователя
class UserHP:
    def __init__(self, screen):
        self.screen = screen
        self.condition_dead = False
        self.n_hp = 0

    # Метод для изменения здоровья в реальном времени
    def update_hp(self, n_shot):
        self.n_hp = amount_user_hp - int(n_shot)
        len_one_hp = position_hp[2] // amount_user_hp - 1

        pygame.draw.rect(self.screen, (0, 0, 0),
                         position_hp)
        if self.n_hp > 0:
            for i in range(self.n_hp):
                pygame.draw.rect(self.screen, (255, 0, 0),
                                 ((len_one_hp + 1) * i + position_hp[0], position_hp[1],
                                  len_one_hp, position_hp[3]))
        else:
            self.condition_dead = True

        pygame.draw.rect(self.screen, (255, 255, 255),
                         position_hp, 1)

    # Проверка, жив пользователь, иначе завершить игру
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

    # Расчёт скорости персонажа (уменьшается пропорциально здоровью)
    def calculate_speed(self):
        speed = int(self.n_hp / amount_user_hp * 3) + 1
        return speed
