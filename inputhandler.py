import libtcodpy as libtcod
from config import *
import logging, game

class InputHandler:
    def __init__(self):
        pass
    def __call__(self, key, mouse):
        #movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            #print "up"
            self.owner.move(0,-1)
            return "playing"
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            #print "down"
            self.owner.move(0,1)
            return "playing"
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            #print "right"
            self.owner.move(1,0)
            return "playing"
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            #print "left"
            self.owner.move(-1,0)
            return "playing"
        elif key.vk == libtcod.KEY_KP9:
            #print "up-right"
            self.owner.move(1,-1)
            return "playing"
        elif key.vk == libtcod.KEY_KP3:
            #print "down-right"
            self.owner.move(1,1)
            return "playing"
        elif key.vk == libtcod.KEY_KP1:
            #print "down-left"
            self.owner.move(-1,1)
            return "playing"
        elif key.vk == libtcod.KEY_KP7:
            #print "up-left"
            self.owner.move(-1,-1)
            return "playing"
        elif key.vk == libtcod.KEY_KP5:
            return "playing"

        elif key.lctrl: #Left CONTROL for debug actions
            key_char = chr(key.c)
            if key_char == 'g': #toggle ghost mode
                if self.owner.ghost:
                    self.owner.ghost = False
                    game.g.message("Ghost mode disabled",C_DEBUG_MSG)
                else:
                    self.owner.ghost = True
                    game.g.message("Ghost mode enabled",C_DEBUG_MSG)
            elif key_char == 'p': #print pos to term
                game.g.message("Player at: " + str(self.owner.pos),C_DEBUG_MSG)
            elif key_char == 'e':
                game.g.dungeon.levels[game.g.cur_level].explore_explorable()
                game.g.message("Level explored",C_DEBUG_MSG)
            elif key_char == 'a': #explore level
                game.g.dungeon.levels[game.g.cur_level].explore_all()
                game.g.message("Level explored",C_DEBUG_MSG)
            elif key_char == 'r': #print room id
                player_pos = self.owner.pos
                room_id = game.g.dungeon.levels[game.g.cur_level].which_room(*player_pos)
                game.g.message("In room: " + str(room_id),C_DEBUG_MSG)
            return "paused"
        return "paused"
