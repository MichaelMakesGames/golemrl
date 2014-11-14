import libtcodpy as libtcod
from config import *
import logging
import game

class AI:
    def __init__(self):
        self.state = "sleeping"
        self.last_saw_player = 0
        self.path = libtcod.path_new_using_map(game.g.dungeon.tcod_map)
        self.player_pos = (0,0)
        

    def update(self):
        tcod_map = game.g.dungeon.tcod_map
        pos = self.owner.pos
        visible = libtcod.map_is_in_fov(tcod_map,*pos)
    
        action_taken = False
        while not action_taken:
            if self.state == "sleeping":
                if visible:
                    self.state = "awake"

            elif self.state == "awake":
                if visible:
                    self.last_saw_player = 0
                else:
                    self.last_saw_player += 1
                    if self.last_saw_player >= 5:
                        self.state = "sleeping"

                new_player_pos = game.g.player.pos
                if self.player_pos != new_player_pos:
                    self.player_pos = new_player_pos
                    libtcod.path_compute(self.path, pos[0], pos[1],
                                         self.player_pos[0],
                                         self.player_pos[1])

                print libtcod.path_size(self.path), self.player_pos
                if libtcod.path_size(self.path) > 0:
                    x,y = libtcod.path_walk(self.path,True)
                    self.owner.move_to(x,y)
                else:
                    self.owner.creature.attack(game.g.player)
                action_taken = True
