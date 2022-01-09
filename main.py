print(0)
import pygame

import player_processing
from sprite_objects import Sprites
from player import Player
from drawing import Drawing, screen, screen_map
from interaction import Interaction
from ray_casting import ray_casting_walls
from map import create_map


def main():
    global user
    all_sprites = pygame.sprite.Group()
    sprites = Sprites()
    clock = pygame.time.Clock()
    player = Player(sprites)
    drawing = Drawing(screen, screen_map, player, clock)
    if not user:
        username = drawing.enter_name()
        user = player_processing.User(username)
    create_map(user.add_player())
    sprites.complication(player_processing.total_highscore)
    drawing.menu()

    interaction = Interaction(player, sprites, drawing, screen)
    interaction.play_music()
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

        if interaction.check_win():
            drawing.win()
        if player.keys_control():
            main()
        if interaction.win_flag:
            if drawing.win():
                user.next_level()
                main()
        user.update_player()

        all_sprites.update(screen)
        pygame.display.flip()
        clock.tick()


if __name__ == '__main__':
    user = None
    main()
