import player_processing
from sprite_objects import *
from player import Player
from drawing import Drawing, screen, screen_map
from interaction import Interaction, play_music
from ray_casting import ray_casting_walls
from health import *


# Головная функция main для осуществления игрового процесса
def main():
    global user

    # Объединение всех спрайтов в группу и запуск таймера pygame
    all_sprites = pygame.sprite.Group()
    sprites = Sprites()
    clock = pygame.time.Clock()

    # Генерация пользователя и информации о нём
    user_hp_ecs = UserHP(screen)
    player = Player(sprites)

    # Прорисовка игрового мира
    drawing = Drawing(screen, screen_map, player, clock, sprites)

    # Проверка, был ли ранее осуществлён вход (чтобы не вводить никнейм несколько раз)
    if not user:
        # Ввод никнейма
        username = drawing.enter_name()
        user = player_processing.User(username)
        user.add_player()

    # Изменение здоровья персонажа в реальном времени
    calculate_hp(user.get_highscore())

    # Расчёт числа генерируемых спрайтов в зависимости от сложности уровня
    sprites.complication(player_processing.total_highscore)

    # Отрисовка главного меню
    drawing.menu()

    # Построеение алгоритмов взаимодействия в зависимости от числа спрайтов
    interaction = Interaction(player, sprites, drawing, screen)

    # Вызов функции проигрывания музыки
    play_music()

    # Отрисовка всех спрайтов
    all_sprites.draw(screen)
    while True:
        # Осуществление передвижения персонажа, обновление его местопололожения в зависимости от скорости
        player.movement()
        player.update_speed(user_hp_ecs.calculate_speed())

        # Отрисовка пространства игрового мира в зависимости от угла камеры
        drawing.background(player.angle)

        # Осуществление выстрела пользователем при нажатии левой кнопки мыши
        walls, wall_shot = ray_casting_walls(player, drawing.textures)

        # Постоянное обновление мини-карты, счётчика fps и убийств
        drawing.world(walls + [obj.object_locate(player) for obj in sprites.list_of_objects])
        drawing.fps(clock)
        drawing.mini_map(player)
        drawing.player_weapon([wall_shot, sprites.sprite_shot])

        # Изменение логики интерактива в зависимости от игровой ситуации:
        # (сколько спрайтов живо, сколько здоровья и т.п.)
        interaction.interaction_objects()
        interaction.npc_action()
        interaction.clear_world()
        interaction.check_win()

        # Обновление здоровья как значения и его счётчика в реальном времени
        user_hp_ecs.update_hp(make_shot())

        # Проверка условий, при которых можно завершить/приостановить игру
        if interaction.check_win():
            drawing.win_or_dead_message(True)
        if player.keys_control():
            main()
        if interaction.win_flag:
            if drawing.win_or_dead_message(True):
                user.next_level(True)
                main()
        if user_hp_ecs.check_dead():
            if drawing.win_or_dead_message(False):
                user.next_level(False)
                main()

        # Работа с базой данных пользователей
        user.update_player()

        # Обновление всех спрайтов
        all_sprites.update(screen)

        # Постоянная смена игровых кадров
        pygame.display.flip()
        clock.tick()


if __name__ == '__main__':
    user = None
    main()
