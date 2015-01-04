import libtcodpy as libtcod
from config import *
import logging

class Tile:
    def __init__(self,tile_type):
        self.tile_type = tile_type
        self.explored = False
        self.item = None
        self.creature = None

    @property
    def tile_type_id(self):
        return self.tile_type.tile_type_id
    @property
    def name(self):
        return self.tile_type.name
    @property
    def char(self):
        return self.tile_type.char
    @property
    def color(self):
        return self.tile_type.color
    @property
    def color_not_visible(self):
        return self.tile_type.color_not_visible
    @property
    def move_through(self):
        return self.tile_type.move_through
    @property
    def see_through(self):
        return self.tile_type.see_through

    def clone(self):
        return Tile(self.tile_type)

    def __repr__(self):
        return self.char
