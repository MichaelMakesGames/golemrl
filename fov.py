import libtcodpy as libtcod
from config import *
import time
import util

class FOV:
    def __init__(self,game,creature):
        self.game = game
        self.creature = creature
        self.fov_map = [[0 for y in range(LEVEL_H)]
                        for x in range(LEVEL_W)]

    @property
    def entity(self):
        return self.creature.owner

    def clear(self):
        self.fov_map = [[0 for y in range(LEVEL_H)]
                        for x in range(LEVEL_W)]

    def refresh(self):
        tcod_map = self.game.dungeon.tcod_map
        if self.entity is self.game.player:
            libtcod.map_compute_fov(tcod_map,
                                    self.entity.x,
                                    self.entity.y,
                                    PLAYER_FOV_RADIUS)
        else:
            libtcod.map_compute_fov(tcod_map,
                                     self.entity.x,
                                     self.entity.y,
                                     self.creature.perception)
        if self.entity is self.game.player:
            for x in range(len(self.fov_map)):
                for y in range(len(self.fov_map[0])):
                    self.fov_map[x][y]=int(libtcod.map_is_in_fov(tcod_map,
                                                                 x,y))
        else:
            self.clear()
            for x in range(self.entity.x-self.creature.perception,
                           self.entity.x+self.creature.perception+1):
                for y in range(self.entity.y-self.creature.perception,
                               self.entity.y+self.creature.perception+1):
                    fov_num = int(libtcod.map_is_in_fov(tcod_map,x,y))
                    if fov_num:
                        if (x-self.entity.x==0 or
                            y-self.entity.y==0 or
                            abs(x-self.entity.x)-abs(y-self.entity.y)==0):
                            fov_num += 1
                        if util.distance(self.entity.x,self.entity.y,x,y)<=self.creature.perception//3:
                            fov_num += 1
                    try:
                        self.fov_map[x][y] = fov_num
                    except IndexError: pass
    def can_see(self,x,y=None):
        if y != None:
            return self.fov_map[x][y]
        else:
            return self.can_see(*x.pos)
    def __call__(self,x,y=None):
        return self.can_see(x,y)
