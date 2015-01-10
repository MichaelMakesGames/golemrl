import libtcodpy as libtcod
from config import *
import util

class FOV:
    def __init__(self,game,creature):
        self.game = game
        self.creature = creature
        self.fov_map = [[0 for y in range(LEVEL_H)]
                        for x in range(LEVEL_W)]

    @property
    def thing(self):
        return self.creature.owner
    def refresh(self):
        tcod_map = self.game.dungeon.tcod_map
        if self.thing is self.game.player:
            libtcod.map_compute_fov(tcod_map,
                                    self.thing.x,
                                    self.thing.y)
        else:
            libtcod.map_compute_fov(tcod_map,
                                     self.thing.x,
                                     self.thing.y,
                                     self.creature.perception*2)

        for x in range(len(self.fov_map)):
            for y in range(len(self.fov_map[0])):
                fov_num = int(libtcod.map_is_in_fov(tcod_map,x,y))
                if fov_num:
                    if (x-self.thing.x==0 or
                        y-self.thing.y==0 or
                        abs(x-self.thing.x)-abs(y-self.thing.y)==0):
                        fov_num += 1
                    if util.distance(self.thing.x,self.thing.y,x,y)<=self.creature.perception:
                        fov_num += 1
                self.fov_map[x][y] = fov_num
    def can_see(self,x,y=None):
        if y != None:
            return self.fov_map[x][y]
        else:
            return self.can_see(*x.pos)
    def __call__(self,x,y=None):
        return self.can_see(x,y)
