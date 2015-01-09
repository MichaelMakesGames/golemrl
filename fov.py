import libtcodpy as libtcod
from config import *

class FOV:
    def __init__(self,game,creature):
        self.game = game
        self.creature = creature
        self.fov_map = [[False for y in range(LEVEL_H)]
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

        for x in range(LEVEL_W):
            for y in range(LEVEL_H):
                self.fov_map[x][y]=libtcod.map_is_in_fov(tcod_map,x,y)

    def can_see(self,x,y):
        return self.fov_map[x][y]
    def __call__(self,x,y):
        return self.can_see(x,y)
