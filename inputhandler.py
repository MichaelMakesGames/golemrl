import libtcodpy as libtcod
from config import *
import logging

from observer import Subject
from event import Event

logger = logging.getLogger('input')

class InputHandler(Subject):
    def __init__(self):
        Subject.__init__(self)
    def __call__(self, key, mouse):
        game = self.owner.owner
        key_char = chr(key.c)
        action_dict = {('r',False): ACTION_HARVEST,
                       ('g',True): ACTION_TOGGLE_GHOST,
                       ('e',True): ACTION_EXPLORE_EXPLORABLE,
                       ('a',True): ACTION_EXPLORE_ALL,
                       ('p',True): ACTION_PRINT_POS,
                       ('r',True): ACTION_PRINT_ROOM,
                       libtcod.KEY_UP: ACTION_MOVE_N,
                       libtcod.KEY_DOWN: ACTION_MOVE_S,
                       libtcod.KEY_RIGHT: ACTION_MOVE_E,
                       libtcod.KEY_LEFT: ACTION_MOVE_W,
                       libtcod.KEY_KP1: ACTION_MOVE_SW,
                       libtcod.KEY_KP2: ACTION_MOVE_S,
                       libtcod.KEY_KP3: ACTION_MOVE_SE,
                       libtcod.KEY_KP4: ACTION_MOVE_W,
                       libtcod.KEY_KP5: ACTION_WAIT,
                       libtcod.KEY_KP6: ACTION_MOVE_E,
                       libtcod.KEY_KP7: ACTION_MOVE_NW,
                       libtcod.KEY_KP8: ACTION_MOVE_N,
                       libtcod.KEY_KP9: ACTION_MOVE_NE}

        action = ACTION_NONE
        try:
            if key_char != '\0':
                action = action_dict[(key_char,key.lctrl)]
            else:
                action = action_dict[key.vk]
        except KeyError: pass

        event = eval(action)
        if event == None:
            event = Event(EVENT_NONE)
            logger.warn('Action %s returned None'%repr(action))

        event_type = event.event_type
        if event_type == EVENT_NONE:
            return STATE_PAUSED
        elif event_type == EVENT_MOVE:
            return STATE_PLAYING
        elif event_type == EVENT_ATTACK:
            return STATE_PLAYING
        elif event_type == EVENT_HARVEST:
            return STATE_PLAYING
        elif event_type == EVENT_WAIT:
            return STATE_PLAYING

        """
        if key.lctrl: #Left CONTROL for debug actions
            if key_char == 'g': #toggle ghost mode
                if self.owner.ghost:
                    self.owner.ghost = False
                    game.message("Ghost mode disabled",C_DEBUG_MSG)
                else:
                    self.owner.ghost = True
                    game.message("Ghost mode enabled",C_DEBUG_MSG)
            elif key_char == 'p': #print pos to term
                game.message("Player at: " + str(self.owner.pos),C_DEBUG_MSG)
            elif key_char == 'e':
                game.cur_level.explore_explorable()
                game.message("Level explored",C_DEBUG_MSG)
            elif key_char == 'a': #explore level
                game.cur_level.explore_all()
                game.message("Level explored",C_DEBUG_MSG)
            elif key_char == 'r': #print room id
                player_pos = self.owner.pos
                room_id = game.cur_level.which_room(*player_pos)
                if room_id == -1:
                    game.message("Not in room",C_DEBUG_MSG)
                else:
                    game.message("Room id: %i, tags: %s" % (room_id,', '.join(game.cur_level.get_room(room_id).tags)), C_DEBUG_MSG)
            return STATE_PAUSED

        #movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            self.owner.move_or_attack(0,-1)
            return STATE_PLAYING
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            self.owner.move_or_attack(0,1)
            return STATE_PLAYING
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            self.owner.move_or_attack(1,0)
            return STATE_PLAYING
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            self.owner.move_or_attack(-1,0)
            return STATE_PLAYING
        elif key.vk == libtcod.KEY_KP9:
            self.owner.move_or_attack(1,-1)
            return STATE_PLAYING
        elif key.vk == libtcod.KEY_KP3:
            self.owner.move_or_attack(1,1)
            return STATE_PLAYING
        elif key.vk == libtcod.KEY_KP1:
            self.owner.move_or_attack(-1,1)
            return STATE_PLAYING
        elif key.vk == libtcod.KEY_KP7:
            self.owner.move_or_attack(-1,-1)
            return STATE_PLAYING
        elif key.vk == libtcod.KEY_KP5:
            return STATE_PLAYING


        else:
            if key_char == 'h':
                event = self.owner.harvest_corpse()
                if event.event_type == EVENT_HARVEST:
                    game.message("Player harvested a corpse!",
                                 event['majority_material'].written_color)
                    return STATE_PLAYING
                elif event.event_type == EVENT_NONE:
                    return STATE_PAUSED

        return STATE_PAUSED
        """
