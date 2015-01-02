import libtcodpy as libtcod
from config import *
import logging

class Cave:
    """Cave class is used as room for map analysis and will later be
    used for monster and item placement as well. It is mostly a just
    holds data for now, and the functions in it are for getting derived
    data"""
    def __init__(self,room_id):
        self.room_id = room_id
        self.tile_positions = []
        self.connections = []
        self.tags = [self.kind.upper()]

    @property
    def kind(self):
        return self.__class__.__name__

    def __iter__(self):
        return iter(self.tile_positions)

    def __len__(self):
        return len(self.tile_positions)

    """min/max_x/y_cells returns a list of coordinates of whatever
    cell(s) have the least or greatest values for their x or y
    coordinates. Note that even if their is one set of coordinates,
    a list is returned. The corresponding min/max_x/y just returns the
    single value instead of the list of coordinates."""
    @property
    def min_x_cells(self):
        min_x = []
        for pos in self.tile_positions:
            if len(min_x) == 0 or pos[0] == min_x[0][0]:
                min_x.append(pos)
            elif pos[0] < min_x[0][0]:
                min_x = [pos]
        return min_x

    @property
    def max_x_cells(self):
        max_x = []
        for pos in self.tile_positions:
            if len(max_x) == 0 or pos[0] == max_x[0][0]:
                max_x.append(pos)
            elif pos[0] > max_x[0][0]:
                max_x = [pos]
        return max_x

    @property
    def min_y_cells(self):
        min_y = []
        for pos in self.tile_positions:
            if len(min_y) == 0 or pos[1] == min_y[0][1]:
                min_y.append(pos)
            elif pos[1] < min_y[0][1]:
                min_y = [pos]
        return min_y

    @property
    def max_y_cells(self):
        max_y = []
        for pos in self.tile_positions:
            if len(max_y) == 0 or pos[1] == max_y[0][1]:
                max_y.append(pos)
            elif pos[1] > max_y[0][1]:
                max_y = [pos]
        return max_y

    @property
    def min_x(self):
        return self.min_x_cells[0][0]
    @property
    def max_x(self):
        return self.max_x_cells[0][0]
    @property
    def min_y(self):
        return self.min_y_cells[0][1]
    @property
    def max_y(self):
        return self.max_y_cells[0][1]

    def add_connection(self,room):
        if room not in self.connections:
            self.connections.append(room)
            room.connections.append(self)

    def connected_to(self,room):
        return room in self.connections

    def tag(self,tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def has_tag(self,tag):
        return tag in self.tags

    def has_tags(self,*tags):
        for tag in tags:
            if tag not in self.tags:
                return False
        return True

    def has_only_tags(self,*tags):
        return has_tags(*tags) and len(tags) == len(self.tags)

class Tunnel(Cave): #just a skinny cave with a different purpose
    pass
