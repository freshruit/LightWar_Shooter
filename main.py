from player import *
from sprite_objects import *
from drawing import *
from interaction import *


def main():
    sprites = Sprites()
    clock = pygame.time.Clock()
    player = Player(sprites)
    drawing = Drawing(screen, screen_map, player, clock)
    drawing.menu()
    interaction = Interaction(player, sprites, drawing, screen)
    interaction.play_music()
    pygame.mouse.set_visible(False)
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

        pygame.display.flip()
        clock.tick()


if __name__ == '__main__':
    main()
