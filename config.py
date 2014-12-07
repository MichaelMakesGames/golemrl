import libtcodpy as libtcod

SCREEN_W=80
SCREEN_H=50

MAP_X=0
MAP_Y=7
MAP_W=50
MAP_H=43

LOG_X=0
LOG_Y=0
LOG_W=50
LOG_H=7

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
C_EFFECT_MSG = libtcod.light_green

#Menus
MENU_HEAL = '''Menu('Heal for 10 Clay',
                    [{'input':('1',False),
                      'name':'Heal head',
                      'action':'self.owner.creature.heal("Head")'},
                     {'input':('2',False),
                      'name':'Heal torso',
                      'action':'self.owner.creature.heal("Torso")'},
                     {'input':('3',False),
                      'name':'Heal left arm',
                      'action':'self.owner.creature.heal("L Arm")'},
                     {'input':('4',False),
                      'name':'Heal right arm',
                      'action':'self.owner.creature.heal("R Arm")'},
                     {'input':('5',False),
                      'name':'Heal left leg',
                      'action':'self.owner.creature.heal("L Leg")'},
                     {'input':('6',False),
                      'name':'Heal right leg',
                      'action':'self.owner.creature.heal("R Leg")'}
                    ] )'''

#Game states
STATE_PLAYING = 'PLAYING'
STATE_PAUSED = 'PAUSED'
STATE_MENU = 'MENU'

#Room tags
TAG_CAVE = 'CAVE'
TAG_TUNNEL = 'TUNNEL'
TAG_SM = 'SMALL'
TAG_MD = 'MEDIUM'
TAG_LG = 'LARGE'
TAG_START = 'START'
TAG_END = 'END'
TAG_PATH = 'PATH'

#Event types
EVENT_NONE = 'NONE'
EVENT_HARVEST = 'HARVEST'
EVENT_ADD_BPEFFECT = 'ADD_BPEFFECT'
EVENT_WAIT = 'WAIT'
EVENT_MOVE = 'MOVE'
EVENT_HEAL = 'HEAL'
EVENT_ATTACK = 'ATTACK'
EVENT_DIE = 'DIE'
EVENT_CREATE = 'CREATE'
EVENT_TOGGLE_GHOST = 'TOGGLE_GHOST'
EVENT_EXPLORE_EXPLORABLE = 'EXPLORE_EXPLORABLE'
EVENT_EXPLORE_ALL = 'EXPLORE_ALL'
EVENT_PRINT_POS = 'PRINT_POS'
EVENT_PRINT_ROOM = 'PRINT_ROOM'
EVENT_MENU_OPEN = 'MENU_OPEN'
EVENT_MENU_CANCEL = 'MENU_CANCEL'

#Actions (temporary)
ACTION_NONE = 'Event(EVENT_NONE)'
ACTION_MOVE_N = 'self.owner.move_or_attack(0,-1)'
ACTION_MOVE_S = 'self.owner.move_or_attack(0,1)'
ACTION_MOVE_E = 'self.owner.move_or_attack(1,0)'
ACTION_MOVE_W = 'self.owner.move_or_attack(-1,0)'
ACTION_MOVE_NE = 'self.owner.move_or_attack(1,-1)'
ACTION_MOVE_NW = 'self.owner.move_or_attack(-1,-1)'
ACTION_MOVE_SE = 'self.owner.move_or_attack(1,1)'
ACTION_MOVE_SW = 'self.owner.move_or_attack(-1,1)'
ACTION_WAIT = 'Event(EVENT_WAIT)'
ACTION_HARVEST = 'self.owner.harvest_corpse()'
ACTION_TOGGLE_GHOST = 'self.owner.toggle_ghost()'
ACTION_EXPLORE_EXPLORABLE = 'self.notify(game.cur_level.explore_explorable())'
ACTION_EXPLORE_ALL = 'self.notify(game.cur_level.explore_all())'
ACTION_PRINT_POS = 'self.notify(Event(EVENT_PRINT_POS, thing=self.owner))'
ACTION_PRINT_ROOM = 'self.notify(Event(EVENT_PRINT_ROOM, pos=self.owner.pos))'
ACTION_OPEN_HEAL_MENU = 'self.set_menu(%s)'%MENU_HEAL
ACTION_CANCEL_MENU = 'self.set_menu(None)'
