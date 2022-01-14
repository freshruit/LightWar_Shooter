import pygame

import player_processing
from sprite_objects import Sprites, cec_n_shot
from player import Player
from drawing import Drawing, screen, screen_map
from interaction import Interaction, play_music
from ray_casting import ray_casting_walls
from hp_user import user_hp



def main():
    global user

    all_sprites = pygame.sprite.Group()
    sprites = Sprites(screen)
    sprites_obgect = cec_n_shot()
    clock = pygame.time.Clock()
    player = Player(sprites)

    user_hp_ecs = user_hp(screen)

    drawing = Drawing(screen, screen_map, player, clock)
    if not user:
        username = drawing.enter_name()
        user = player_processing.User(username)
        user.add_player()
    sprites.complication(player_processing.total_highscore)
    drawing.menu()

    interaction = Interaction(player, sprites, drawing, screen)
    play_music()
    all_sprites.draw(screen)
    while True:
        player.movement()
        drawing.background(player.angle)
        walls, wall_shot = ray_casting_walls(player, drawing.textures)
        drawing.world(walls + [obj.object_locate(player) for obj in sprites.list_of_objects])
        drawing.fps(clock)
        drawing.mini_map(player)
        drawing.player_weapon([wall_shot, sprites.sprite_shot])

        interaction.interaction_objects()
        interaction.npc_action()
        interaction.clear_world()
        interaction.check_win()

        user_hp_ecs.apdate_hp(sprites_obgect.cec_shot())

        if interaction.check_win():
            drawing.win_dead(True)
        if player.keys_control():
            main()
        if interaction.win_flag:
            if drawing.win_dead(True):
                n_shot = 0
                user.next_level(True)
                main()

        if user_hp_ecs.check_dead():
            if drawing.win_dead(False):
                n_shot = 0
                user.next_level(False)
                main()

        user.update_player()
        all_sprites.update(screen)
        pygame.display.flip()
        clock.tick()


if __name__ == '__main__':
    user = None
    main()
