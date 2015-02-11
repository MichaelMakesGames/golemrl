import libtcodpy as libtcod

PLAYER_FOV_RADIUS = 10

FOCUS_PLAYER = 'PLAYER'
FOCUS_FIXED = 'FIXED'
FOCUS = FOCUS_FIXED

SCREEN_W=106
SCREEN_H=70

MAP_X=20
MAP_Y=0
MAP_W=86
MAP_H=52

LOG_X=0
LOG_Y=52
LOG_W=106
LOG_H=18

PANEL_X=0
PANEL_Y=0
PANEL_W=20
PANEL_H=52

LIMIT_FPS=30
SHOW_FPS=True

NUM_LEVELS = 10
LEVEL_W = 84
LEVEL_H = 50

WALL_ID = 'WALL'
FLOOR_ID = 'FLOOR'

C_BORDER = libtcod.lighter_gray
C_BORDER_BKGND = libtcod.black
C_MENU = libtcod.lightest_gray

CORPSE_CHAR = '%'
C_CORPSE = libtcod.dark_red

LOG_FADE = 0.75
C_DEBUG_MSG = libtcod.light_blue
C_COMBAT_MSG = libtcod.light_red
C_EFFECT_MSG = libtcod.light_green

DICE_SIDES = 6
DEGREE_OF_SUCCESS = 5

ENERGY_THRESHOLD = 60

#Game states
STATE_PLAYING = 'PLAYING'
STATE_PAUSED = 'PAUSED'
STATE_MENU = 'MENU'

#Input states
INPUT_NORMAL      = 'NORMAL'
INPUT_BP          = 'BP'
INPUT_DIRECTION_4 = 'DIRECTION_4'
INPUT_DIRECTION_8 = 'DIRECTION_8'
INPUT_DIRECTION   = 'DIRECTION'

#Map overlays
OVERLAY_FOV = 'FOV'

#AI states
AI_INACTIVE = 'INACTIVE'
AI_SLEEPING = 'SLEEPING'
AI_RESTING  = 'RESTING'
AI_WANDERING= 'WANDERING'
AI_FIGHTING = 'FIGHTING'
AI_FLEEING  = 'FLEEING'

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
EVENT_INSCRIBE = 'INSCRIBE'
EVENT_ERASE = 'ERASE'
EVENT_ADD_TRAIT = 'ADD_TRAIT'
EVENT_REMOVE_TRAIT = 'REMOVE_TRAIT'
EVENT_WAKE_UP = 'WAKE_UP'
EVENT_NOTICE = 'NOTICE'
EVENT_STUMBLE = 'STUMBLE'
EVENT_HEAR = 'HEAR'
EVENT_ACTIVATE = 'ACTIVATE'
EVENT_USE = 'USE' #representing an active ability use which counts as a turn; returned by some ability events
EVENT_RESOLVE_ABILITY = 'RESOLVE_ABILITY'
#for dealing with abilities requiring input
EVENT_DIRECTION = 'DIRECTION'
EVENT_CANCEL = 'CANCEL'

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
ACTION_ACTIVATE_N = 'self.owner.complete_ability((0,-1))'
ACTION_ACTIVATE_S = 'self.owner.complete_ability((0,1))'
ACTION_ACTIVATE_E = 'self.owner.complete_ability((1,0))'
ACTION_ACTIVATE_W = 'self.owner.complete_ability((-1,0))'
ACTION_ACTIVATE_NE = 'self.owner.complete_ability((1,-1))'
ACTION_ACTIVATE_NW = 'self.owner.complete_ability((-1,-1))'
ACTION_ACTIVATE_SE = 'self.owner.complete_ability((1,1))'
ACTION_ACTIVATE_SW = 'self.owner.complete_ability((-1,1))'
ACTION_CANCEL_ABILITY = 'self.owner.cancel_ability()'
ACTION_HARVEST = 'self.owner.harvest_corpse()'
ACTION_TOGGLE_GHOST = 'self.owner.toggle_ghost()'
ACTION_EXPLORE_EXPLORABLE = 'self.notify(self.game.cur_level.explore_explorable())'
ACTION_EXPLORE_ALL = 'self.notify(self.game.cur_level.explore_all())'
ACTION_PRINT_POS = 'self.notify(Event(EVENT_PRINT_POS, entity=self.owner))'
ACTION_PRINT_ROOM = 'self.notify(Event(EVENT_PRINT_ROOM, pos=self.owner.pos))'
ACTION_CANCEL_MENU = 'self.set_menu(None)'
ACTION_OPEN_SPELL_MENU = 'self.open_spell_menu()'
ACTION_OPEN_BODY_MENU = 'self.open_body_menu()'
ACTION_TOGGLE_OVERLAY_FOV = 'self.toggle_overlay(OVERLAY_FOV)'
ACTION_HEAL = 'self.owner.notify(Event(EVENT_ACTIVATE, actor=self.owner, ability=self.game.abilities["HEAL"]))'
ACTION_CHARGE = 'self.owner.notify(Event(EVENT_ACTIVATE, actor=self.owner, ability=self.game.abilities["CHARGE"]))'
ACTION_DODGE = 'self.owner.notify(Event(EVENT_ACTIVATE, actor=self.owner, ability=self.game.abilities["DODGE"]))'
#Extra input actions
ACTION_CANCEL = 'self.owner.notify(Event(EVENT_CANCEL,actor=self.owner))'
#INPUT_DIRECTION_4/8 actions
ACTION_DIRECTION_N  = 'self.owner.notify(Event(EVENT_DIRECTION,actor=self.owner, direction=(0,-1)))'
ACTION_DIRECTION_NE = 'self.owner.notify(Event(EVENT_DIRECTION,actor=self.owner, direction=(1,-1)))'
ACTION_DIRECTION_E  = 'self.owner.notify(Event(EVENT_DIRECTION,actor=self.owner, direction=(1,0)))'
ACTION_DIRECTION_SE = 'self.owner.notify(Event(EVENT_DIRECTION,actor=self.owner, direction=(1,1)))'
ACTION_DIRECTION_S  = 'self.owner.notify(Event(EVENT_DIRECTION,actor=self.owner, direction=(0,1)))'
ACTION_DIRECTION_SW = 'self.owner.notify(Event(EVENT_DIRECTION,actor=self.owner, direction=(-1,1)))'
ACTION_DIRECTION_W  = 'self.owner.notify(Event(EVENT_DIRECTION,actor=self.owner, direction=(-1,0)))'
ACTION_DIRECTION_NW = 'self.owner.notify(Event(EVENT_DIRECTION,actor=self.owner, direction=(-1,-1)))'
ACTION_DIRECTION_NONE = 'self.owner.notify(Event(EVENT_DIRECTION,actor=self.owner, direction=(0,0)))'
