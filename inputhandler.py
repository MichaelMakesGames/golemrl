import libtcodpy as libtcod
from config import *
import logging

class InputHandler:
    def __init__(self):
        pass
    def __call__(self, key, mouse):
        game = self.owner.owner
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

        elif key.lctrl: #Left CONTROL for debug actions
            key_char = chr(key.c)
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

        else:
            key_char = chr(key.c)
            if key_char == 'h':
                event = self.owner.harvest_corpse()
                if event.event_type == EVENT_HARVEST:
                    game.message("Player harvested a corpse!",
                                 event['majority_material'].written_color)
                    return STATE_PLAYING
                elif event.event_type == EVENT_NONE:
                    return STATE_PAUSED

        return STATE_PAUSED
