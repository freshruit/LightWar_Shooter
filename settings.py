import math

# Настройки игры
WIDTH = 1200
HEIGHT = 800
FPS = 60
SMOOTHNESS = 100
FPS_COUNTER_POSITION = (WIDTH - 65, 5)

# Настройки карты
MAP_SCALE = 5
MAP_SMOOTHNESS = SMOOTHNESS // MAP_SCALE
MAP_POSITION = (0, 0)

# Настройки визуализации
FIELD_OF_VIEW = math.pi / 3
COUNT_RAYS = 300
MAX_DEPTH = 800
DIFFERENCE_ANGLE = FIELD_OF_VIEW / COUNT_RAYS
DISTANCE = COUNT_RAYS / (2 * math.tan(FIELD_OF_VIEW / 2))
DISTANCE_SCALE = WIDTH // COUNT_RAYS
REMOTENESS = DISTANCE * SMOOTHNESS

# Настройки игрока
player_position = (WIDTH // 2, HEIGHT // 2)
player_angle = 0
player_speed = 2
