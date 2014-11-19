import libtcodpy as libtcod

SCREEN_W=80
SCREEN_H=50

MAP_X=0
MAP_Y=5
MAP_W=50
MAP_H=45

LOG_X=0
LOG_Y=0
LOG_W=50
LOG_H=5

PANEL_X=50
PANEL_Y=0
PANEL_W=30
PANEL_H=50

LIMIT_FPS=30

NUM_LEVELS = 10
LEVEL_W = 50
LEVEL_H = 50

EXPERIMENTAL_WALLS = True

WALL_CHAR = '#'
C_WALL = libtcod.dark_sepia
C_WALL_BKGND = libtcod.darker_sepia
C_WALL_UNSEEN = libtcod.dark_gray
C_WALL_BKGND_UNSEEN = libtcod.darker_gray

FLOOR_CHAR = '.'
C_FLOOR = libtcod.sepia
C_FLOOR_BKGND = libtcod.light_sepia
C_FLOOR_UNSEEN = libtcod.gray
C_FLOOR_BKGND_UNSEEN = libtcod.light_gray

C_BORDER = libtcod.light_gray
C_BORDER_BKGND = libtcod.black

CORPSE_CHAR = '%'
C_CORPSE = libtcod.dark_red

LOG_FADE = 0.75
C_DEBUG_MSG = libtcod.light_blue
C_COMBAT_MSG = libtcod.light_red

#Room tags
TAG_CAVE = 'cave'
TAG_TUNNEL = 'tunnel'
TAG_SM = 'small'
TAG_MD = 'medium'
TAG_LG = 'large'
TAG_START = 'start'
TAG_END = 'end'
TAG_PATH = 'path'
