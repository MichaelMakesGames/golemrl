import libtcodpy as libtcod
from config import *
import logging, random

class Tile:
    def __init__(self,tile_type):
        self.tile_type = tile_type
        self.explored = False
        self.item = None
        self.creature = None
        if type(self.tile_type.char) == list:
            self.char_variety = random.randrange(len(self.tile_type.char))
        else:
            self.char_variety=0
        if type(self.tile_type.color) == list:
            self.color_variety=random.randrange(len(self.tile_type.color))
        else:
            self.color_variety=0

    @property
    def tile_type_id(self):
        return self.tile_type.tile_type_id
    @property
    def name(self):
        return self.tile_type.name
    @property
    def char(self):
        c = self.tile_type.char
        if type(c)==list:
            return c[self.char_variety]
        else:
            return c
    @property
    def color(self):
        c = self.tile_type.color
        if type(c)==list:
            return c[self.color_variety]
        else:
            return c
    @property
    def color_not_visible(self):
        return self.tile_type.color_not_visible
    @property
    def move_through(self):
        return self.tile_type.move_through
    @property
    def see_through(self):
        return self.tile_type.see_through

    def change_type(self,tile_type):
        self.tile_type=tile_type
        if type(self.tile_type.char) == list:
            self.char_variety = random.randrange(len(self.tile_type.char))
        else:
            self.char_variety=0
        if type(self.tile_type.color) == list:
            self.color_variety=random.randrange(len(self.tile_type.color))
        else:
            self.color_variety=0

    def clone(self):
        return Tile(self.tile_type)

    def __repr__(self):
        return self.char
