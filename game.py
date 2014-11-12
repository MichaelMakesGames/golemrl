import libtcodpy as libtcod
from config import *
import logging
import textwrap
from gameobject import GameObject
from inputhandler import InputHandler
from physics import Physics
from creature import Creature
from dungeon import Dungeon
from console import Console

class Game:
    def __init__(self, player, game_objects, dungeon, message_log,
                 cur_level = 0, state = "playing"):
        self.player = player
        self.player.owner = self

        self.game_objects = game_objects
        for obj in self.game_objects:
            obj.owner = self
        self.game_objects.insert(0,self.player)

        self.dungeon = dungeon
        self.dungeon.owner = self

        self.message_log = message_log

        self.map_con = Console("Dungeon Map",MAP_X,MAP_Y,MAP_W,MAP_H)
        self.panel_con = Console("Side Panel",PANEL_X,PANEL_Y,PANEL_W,PANEL_H)
        self.log_con = Console("Message Log",LOG_X,LOG_Y,LOG_W,LOG_H)

        self.cur_level = cur_level
        self.state = state

    def message(self,message,color):
        print message
        message_lines = textwrap.wrap(message, self.log_con.w-2)
        for line in message_lines:
            self.message_log.append((line,color))

    def clear_all(self):
        for game_object in self.game_objects:
            game_object.clear(self.player.physics_comp.x,
                              self.player.physics_comp.y,
                              self.map_con)

    def render_panel(self):
        self.panel_con.draw_border(True,C_BORDER,C_BORDER_BKGND)

    def render_log(self):
        self.log_con.clear()
        for i in range(self.log_con.h-2):
            try:
                text, color = self.message_log[-(i+1)]
                color = make_darker_color(color,i*LOG_FADE/(self.log_con.h-3))
                for j in range(len(text)):
                    self.log_con.put_char(j+1,self.log_con.h-2-i,text[j],color)
            except:
                pass
        
        self.log_con.draw_border(True,C_BORDER,C_BORDER_BKGND)


    def render_all(self):
        player_x = self.player.physics_comp.x
        player_y = self.player.physics_comp.y
        #print player_x, player_y
        self.dungeon.render(self.cur_level,
                            player_x,
                            player_y,
                            self.map_con)
        for game_object in self.game_objects:
            if game_object != self.player:
                game_object.render(player_x, player_y, self.map_con)
        self.player.render(player_x, player_y, self.map_con)
        self.map_con.draw_border(True,C_BORDER,C_BORDER_BKGND)
        self.map_con.blit()

        self.render_log()
        self.log_con.blit()

        self.render_panel()
        self.panel_con.blit()

    def play(self):
        key = libtcod.Key()
        mouse = libtcod.Mouse()

        while not libtcod.console_is_window_closed():
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
            self.clear_all()

            player_prev_pos = self.player.physics_comp.pos
            self.player.input_handler(key,mouse)
            if self.player.physics_comp.pos != player_prev_pos:
                self.dungeon.send("player_moved")

            if self.state == "playing":
                for game_object in self.game_objects:
                    game_object.update()

            self.dungeon.update()

            self.render_all()
            libtcod.console_flush()

g = None

def new_game(seed = 0xDEADBEEF):
    global g

    dungeon = Dungeon(seed)
    player_x,player_y = dungeon.levels[0].get_start_pos()
    player_physics_comp = Physics(player_x, player_y, dungeon.levels[0], False, True)
    player_creature_comp = Creature('Player','@',libtcod.white,3,10)
    player = GameObject(obj_id = 0,
                        physics_comp = player_physics_comp,
                        creature_comp = player_creature_comp)
    player.input_handler = InputHandler()
    player.input_handler.owner = player
    g = Game(player, [], dungeon, [])

    mon1_physics_comp = Physics(5,26,dungeon.levels[0],False,True)
    mon1_creature_comp = Creature('Animate Clay','c',libtcod.darkest_sepia,1,5)
    mon1 = GameObject(obj_id = 1,
                      physics_comp = mon1_physics_comp,
                      creature_comp = mon1_creature_comp)
    g.game_objects.append(mon1)

def load_game(file_name):
    pass

def save_game(file_name):
    pass

def make_darker_color(color,percent):
    if type(percent) == int:
        percent = percent/100
    if percent > 1.0:
        percent = 1.0
    new_r = color['r'] - int(percent*color['r'])
    new_g = color['g'] - int(percent*color['g'])
    new_b = color['b'] - int(percent*color['b'])
    return libtcod.Color(new_r,new_g,new_b)
