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
        pos = self.owner.physics_comp.pos
        visible = libtcod.map_is_in_fov(tcod_map,*pos)

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

            new_player_pos = game.g.player.physics_comp.pos
            if self.player_pos != new_player_pos:
                self.player_pos = new_player_pos
                libtcod.path_compute(self.path, pos[0], pos[1],
                                     self.player_pos[0],
                                     self.player_pos[1])

            x,y = libtcod.path_walk(self.path,True)

            if x:
                self.owner.physics_comp.move_to(x,y)

            elif (abs(pos[0]-self.player_pos[0]) <= 1 and
                  abs(pos[1]-self.player_pos[1]) <= 1):
                self.owner.creature_comp.attack(game.g.player)
