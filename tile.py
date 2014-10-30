import libtcodpy as libtcod
from config import *
import logging

class Tile:
    def __init__(self, char=WALL_CHAR,
                 color=C_WALL, color_unseen = C_WALL_UNSEEN,
                 bkgnd=C_WALL_BKGND, bkgnd_unseen=C_WALL_BKGND_UNSEEN,
                 move_through=False, see_through=False):
        self.char = char
        self.color = color
        self.color_unseen = color_unseen
        self.bkgnd = bkgnd
        self.bkgnd_unseen = bkgnd_unseen
        self.move_through = move_through
        self.see_through = see_through
        self.explored = False

    def clone(self):
        return Tile(self.char,
                    self.color,self.color_unseen,
                    self.bkgnd,self.bkgnd_unseen,
                    self.move_through,self.see_through)

    def is_floor(self):
        return self.move_through and self.see_through

    def make_floor(self):
        self.char = FLOOR_CHAR
        self.color = C_FLOOR
        self.color_unseen = C_FLOOR_UNSEEN
        self.bkgnd = C_FLOOR_BKGND
        self.bkgnd_unseen = C_FLOOR_BKGND_UNSEEN
        self.move_through = True
        self.see_through = True

    def is_wall(self):
        return (not self.move_through) and (not self.see_through)

    def make_wall(self):
        self.char = WALL_CHAR
        self.color = C_WALL
        self.color_unseen = C_WALL_UNSEEN
        self.bkgnd = C_WALL_BKGND
        self.bkgnd_unseen = C_WALL_BKGND_UNSEEN
        self.move_through = False
        self.see_through = False

    def __repr__(self):
        return self.char
