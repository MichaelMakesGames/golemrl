import libtcodpy as libtcod
from config import *
import logging
import game

class Physics:
    def __init__(self, x, y, level, move_through, see_through):
        self.x = x
        self.y = y
        self.level = level
        self.move_through = move_through
        self.see_through = see_through
        self.ghost = False

    @property
    def pos(self):
        return (self.x,self.y)

    def move_to(self, new_x, new_y):
        if (new_x >= self.level.first_col and
            new_x <= self.level.last_col and
            new_y >= self.level.first_row and
            new_y <= self.level.last_row):
            obj_positions = [obj.physics_comp.pos for obj in game.g.game_objects]
            if (self.level(new_x,new_y).move_through and
                (new_x,new_y) not in obj_positions) or self.ghost:
                self.x = new_x
                self.y = new_y
                if self.owner.creature_comp:
                    game.g.game_map.send('creature_moved')

    def move(self, dx, dy):
        self.move_to(self.x+dx, self.y+dy)

    def update(self):
        pass
