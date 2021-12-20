from settings import *

level_1 = ['WWWWWWWWWWWW',
           'W......W...W',
           'W..WWW...W.W',
           'W....W..WW.W',
           'W..W....W..W',
           'W..W...WWW.W',
           'W....W.....W',
           'WWWWWWWWWWWW']

world_map = set()
mini_map = set()
for i, row in enumerate(level_1):
    for j, wall in enumerate(row):
        if wall == 'W':
            world_map.add((j * SMOOTHNESS, i * SMOOTHNESS))
            mini_map.add((j * MAP_SMOOTHNESS, i * MAP_SMOOTHNESS))
