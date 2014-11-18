import libtcodpy as libtcod
from config import *
import logging
import textwrap
from thing import Thing
from inputhandler import InputHandler
from creature import Creature
from ai import AI
from dungeon import Dungeon
from console import Console

class Game:
    def __init__(self):
        self.player = None
        self.things = []
        self.dungeon = None
        self.message_log = []

        self.map_con = Console("Dungeon Map",MAP_X,MAP_Y,MAP_W,MAP_H)
        self.panel_con = Console("Side Panel",PANEL_X,PANEL_Y,PANEL_W,PANEL_H)
        self.log_con = Console("Message Log",LOG_X,LOG_Y,LOG_W,LOG_H)

        self.state = "playing"

    @property
    def depth(self):
        return self.player.depth
    @property
    def cur_level(self):
        return self.player.level

    def message(self,message,color):
        print message
        logging.getLogger('message').info(message)
        message_lines = textwrap.wrap(message, self.log_con.w-2)
        for line in message_lines:
            self.message_log.append((line,color))

    def add_thing(self,thing):
        thing.owner = self
        self.things.append(thing)

    def next_id(self):
        next_id = 0
        id_list = [thing.obj_id for thing in self.things]
        while True:
            if next_id not in id_list:
                return next_id
            else:
                next_id += 1

    def clear_all(self):
        for thing in self.things:
            thing.clear(self.player.x,
                        self.player.y,
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
        player_x = self.player.x
        player_y = self.player.y

        self.dungeon.render(player_x, player_y, self.map_con)
        for thing in self.things:
            if thing != self.player:
                thing.render(player_x, player_y, self.map_con)
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

            player_prev_pos = self.player.pos
            self.state = self.player.input_handler(key,mouse)
            if self.player.pos != player_prev_pos:
                self.dungeon.send("player_moved")

            if self.state == "playing":
                for thing in self.things:
                    thing.update()
                self.state = "paused"

            self.dungeon.update()

            self.render_all()
            libtcod.console_flush()

def new_game(seed = 0xDEADBEEF):
    game = Game()

    dungeon = Dungeon(seed)
    dungeon.owner = game
    game.dungeon = dungeon
    game.dungeon.levels[0].populate_rooms()

    player_x,player_y = dungeon.levels[0].get_start_pos()
    player_creature_comp = Creature('Player','@',libtcod.white,3,10)
    player = Thing(0,
                   player_x, player_y, 0, False, True,
                   creature = player_creature_comp)

    player.input_handler = InputHandler()
    player.input_handler.owner = player
    game.player = player
    game.add_thing(player)

    return game

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
