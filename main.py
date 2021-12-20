import pygame
from settings import *
from player import Player
from drawing import Drawing


def main():
    pygame.init()
    pygame.display.set_caption('Light War')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen_map = pygame.Surface((WIDTH // MAP_SCALE, HEIGHT // MAP_SCALE))

    player = Player()
    drawing = Drawing(screen, screen_map)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        player.movement()
        screen.fill((0, 0, 0))

        drawing.draw_background()
        drawing.visualize_world(player.position, player.angle)
        drawing.display_fps(clock)
        drawing.make_min_map(player)

        clock.tick()
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
